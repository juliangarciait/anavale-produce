# -*- coding: utf-8 -*-
#############################################################################
#
#    Bassam Infotech LLP
#
#    Copyright (C) 2020-2020 Bassam Infotech LLP (<https://www.bassaminfotech.com>).
#    Author: Mihran Thalhath (mihranthalhath@gmail.com) (mihranz7@gmail.com)
#
#############################################################################

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from collections import defaultdict

_logger = logging.getLogger(__name__)

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
}


# Let's make a copy of account.payment.register for our use case
class AccountCustomRegisterPayment(models.TransientModel):
    _name = 'account.custom.payment.register'
    _description = 'Register Payment'

    payment_date = fields.Date(required=True, default=fields.Date.context_today)
    journal_id = fields.Many2one('account.journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True,
                                        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"
                                        "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n"
                                        "Check: Pay bill by check and print it from Odoo.\n"
                                        "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit, module account_batch_payment must be installed.\n"
                                        "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
    invoice_ids = fields.Many2many('account.move', 'account_invoice_custom_payment_rel_transient', 'payment_id', 'invoice_id', string="Invoices", copy=False, readonly=True)
    group_payment = fields.Boolean(help="Only one payment will be created by partner (bank)/ currency.", default=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
        readonly=True, store=True,
        help='Utility field to express amount currency')
    total_invoice_amount = fields.Monetary(string='Total', currency_field="company_currency_id", compute='_compute_total_invoice_amount')
    partner_id = fields.Many2one('res.partner', string='Partner')
    invoice_type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
    ], string='Invoice Type')
    register_line_ids = fields.One2many('account.payment.register.line', 'account_payment_register_id', string='Lines')
    is_initial = fields.Boolean(string='Is Initial?', default=False)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """ Prepare the dict of values to balance the move.

            :param recordset move: the account.move to link the move line
            :param dict move: a dict of vals of a account.move which will be created later
            :param float amount: the amount of transaction that wasn't already reconciled
        """
        for record in self:
            # If the onchange is not getting triggered for the first time, add the open invoices against the partner
            if not record.is_initial:
                if record.partner_id:
                    invoice_ids = self.env['account.move'].search([
                        ('partner_id', '=', record.partner_id.id),
                        ('type', '=', record.invoice_type),
                        ('state', '=', 'posted'),
                        ('invoice_payment_state', '=', 'not_paid'),
                    ], order='invoice_date_due, date')
                    line_values = []
                    for each_move in invoice_ids:
                        values = (0, 0, {
                            'move_id': each_move.id,
                            'amount_payment': 0.0,
                            'partner_id': each_move.partner_id.id,
                        })
                        line_values.append(values)
                    # Write the new values after unlinking existing lines
                    record.register_line_ids.unlink()
                    record.write({
                        'register_line_ids': line_values,
                        'group_payment': True,
                    })
                else:
                    # If there is no partner, unlink all the lines.
                    # For some reason partner_id and is_initial is getting reset. So set both of them as False
                    # TODO: Check whether above issue is fixable
                    record.register_line_ids.unlink()
                    record.write({
                        'partner_id': False,
                        'is_initial': False,
                        'group_payment': False,
                    })
            # onchange is getting triggered for the first time, so add the invoices in context to the lines
            else:
                record.is_initial = False
                active_ids = self._context.get('active_ids')
                if active_ids:
                    move_ids = self.env['account.move'].search([
                        ('id', 'in', active_ids)
                    ], order='invoice_date_due, date')
                    line_values = []
                    for each_move in move_ids:
                        values = (0, 0, {
                            'move_id': each_move.id,
                            'amount_payment': 0.0,
                            'partner_id': each_move.partner_id.id,
                        })
                        line_values.append(values)
                    record.register_line_ids = line_values

    @api.depends('register_line_ids.amount_payment')
    def _compute_total_invoice_amount(self):
        for record in self:
            total_invoice_amount = 0
            for each_line in record.register_line_ids:
                total_invoice_amount += each_line.amount_payment
            record.total_invoice_amount = total_invoice_amount

    @api.model
    def default_get(self, fields):
        rec = super(AccountCustomRegisterPayment, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        if not active_ids:
            return rec
        # Set is_initial as true to not trigger onchange changes for the first time.
        rec['is_initial'] = True
        invoices = self.env['account.move'].browse(active_ids)
        partner_ids = invoices.mapped('partner_id')
        # Set group payment as false if invoices with different partners are selected
        if len(partner_ids) > 1:
            rec['group_payment'] = False
        else:
            rec['partner_id'] = partner_ids.id
        # Check all invoices are open
        if any(invoice.state != 'posted' or invoice.invoice_payment_state != 'not_paid' or not invoice.is_invoice() for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))
        # Check all invoices are inbound or all invoices are outbound
        outbound_list = [invoice.is_outbound() for invoice in invoices]
        first_outbound = invoices[0].is_outbound()
        if any(x != first_outbound for x in outbound_list):
            raise UserError(_("You can only register at the same time for payment that are all inbound or all outbound"))
        if any(inv.company_id != invoices[0].company_id for inv in invoices):
            raise UserError(_("You can only register at the same time for payment that are all from the same company"))
        # Check the destination account is the same
        destination_account = invoices.line_ids.filtered(lambda line: line.account_internal_type in ('receivable', 'payable')).mapped('account_id')
        if len(destination_account) > 1:
            raise UserError(_('There is more than one receivable/payable account in the concerned invoices. You cannot group payments in that case.'))
        if 'invoice_ids' not in rec:
            rec['invoice_ids'] = [(6, 0, invoices.ids)]
        if 'journal_id' not in rec:
            rec['journal_id'] = self.env['account.journal'].search([('company_id', '=', self.env.company.id), ('type', 'in', ('bank', 'cash'))], limit=1).id
        if 'payment_method_id' not in rec:
            if invoices[0].is_inbound():
                domain = [('payment_type', '=', 'inbound')]
            else:
                domain = [('payment_type', '=', 'outbound')]
            rec['payment_method_id'] = self.env['account.payment.method'].search(domain, limit=1).id
        return rec

    @api.onchange('journal_id', 'invoice_ids')
    def _onchange_journal(self):
        active_ids = self._context.get('active_ids')
        invoices = self.env['account.move'].browse(active_ids)
        if self.journal_id and invoices:
            if invoices[0].is_inbound():
                domain_payment = [('payment_type', '=', 'inbound'), ('id', 'in', self.journal_id.inbound_payment_method_ids.ids)]
            else:
                domain_payment = [('payment_type', '=', 'outbound'), ('id', 'in', self.journal_id.outbound_payment_method_ids.ids)]
            domain_journal = [('type', 'in', ('bank', 'cash')), ('company_id', '=', invoices[0].company_id.id)]
            return {'domain': {'payment_method_id': domain_payment, 'journal_id': domain_journal}}
        return {}

    def _prepare_communication(self, invoices):
        '''Define the value for communication field
        Append all invoice's references together.
        '''
        return " ".join(i.invoice_payment_ref or i.ref or i.name for i in invoices)

    def _prepare_payment_vals(self, invoices):
        '''Create the payment values.

        :param invoices: The invoices/bills to pay. In case of multiple
            documents, they need to be grouped by partner, bank, journal and
            currency.
        :return: The payment values as a dictionary.
        '''
        amount = self.env['account.payment']._compute_payment_amount(invoices, invoices[0].currency_id, self.journal_id, self.payment_date)
        # If grouped payment, find the move ids
        if self.group_payment:
            invoice_ids = []
            for each_line in self.register_line_ids:
                invoice_ids.append(each_line.move_id.id)
            values = {
                'journal_id': self.journal_id.id,
                'payment_method_id': self.payment_method_id.id,
                'payment_date': self.payment_date,
                'communication': self._prepare_communication(invoices),
                'invoice_ids': [(6, 0, invoice_ids)],
                'payment_type': ('inbound' if amount > 0 else 'outbound'),
                'amount': self.total_invoice_amount,
                'currency_id': invoices[0].currency_id.id,
                'partner_id': invoices[0].commercial_partner_id.id,
                'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
                'partner_bank_account_id': invoices[0].invoice_partner_bank_id.id,
            }
        else:
            values = {
                'journal_id': self.journal_id.id,
                'payment_method_id': self.payment_method_id.id,
                'payment_date': self.payment_date,
                'communication': self._prepare_communication(invoices),
                'invoice_ids': [(6, 0, invoices.ids)],
                'payment_type': ('inbound' if amount > 0 else 'outbound'),
                'amount': self.register_line_ids.filtered(lambda x : x.move_id == invoices[0]).amount_payment,
                'currency_id': invoices[0].currency_id.id,
                'partner_id': invoices[0].commercial_partner_id.id,
                'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
                'partner_bank_account_id': invoices[0].invoice_partner_bank_id.id,
            }
        return values

    def _get_payment_group_key(self, invoice):
        """ Returns the grouping key to use for the given invoice when group_payment
        option has been ticked in the wizard.
        """
        return (invoice.commercial_partner_id, invoice.currency_id, invoice.invoice_partner_bank_id, MAP_INVOICE_TYPE_PARTNER_TYPE[invoice.type])

    def get_payments_vals(self):
        '''Compute the values for payments.

        :return: a list of payment values (dictionary).
        '''
        grouped = defaultdict(lambda: self.env["account.move"])
        for inv in self.invoice_ids:
            if self.group_payment:
                grouped[self._get_payment_group_key(inv)] += inv
            else:
                grouped[inv.id] += inv
        return [self._prepare_payment_vals(invoices) for invoices in grouped.values()]

    def create_payments(self):
        '''Create payments according to the invoices.
        Having invoices with different commercial_partner_id or different type
        (Vendor bills with customer invoices) leads to multiple payments.
        In case of all the invoices are related to the same
        commercial_partner_id and have the same type, only one payment will be
        created.

        :return: The ir.actions.act_window to show created payments.
        '''
        selected_move_ids = []
        partner_ids = self.register_line_ids.mapped('move_id.partner_id.id')
        if len(partner_ids) > 1 and self.group_payment:
            raise UserError(_("You can't group payments when invoices with different partners are selected!"))
        for each_record in self.register_line_ids:
            if each_record.move_id.id in selected_move_ids:
                raise UserError(_("You can't select an invoice/bill multiple times!"))
            else:
                selected_move_ids.append(each_record.move_id.id)
        if not self.register_line_ids:
            raise UserError(_("No Invoices selected!"))
        currency_ids = self.register_line_ids.mapped('move_id.currency_id.id')
        if len(currency_ids) > 1 or currency_ids[0] != self.env.company.currency_id.id:
            raise UserError(_("Sorry! We do not support multi currency as of now!"))
        move_ids = self.register_line_ids.mapped('move_id')
        if any(inv.company_id != move_ids[0].company_id for inv in move_ids):
            raise UserError(_("You can only register at the same time for payment that are all from the same company"))
        move_types = set(self.register_line_ids.mapped('move_id.type'))
        if len(move_types) > 1 or self.invoice_type not in move_types:
            raise UserError(_("You can only register at the same time for payment that are all inbound or all outbound"))
        Payment = self.env['account.payment']
        payments = Payment.create(self.get_payments_vals())
        # If grouped payment, use our methods, else use base ones
        if self.group_payment:
            payment_amounts = {}
            invoice_ids = []
            for each_line in self.register_line_ids:
                payment_amounts[each_line.move_id.id] = each_line.amount_payment
                invoice_ids.append(each_line.move_id.id)
            invoices = self.env['account.move'].search([
                ('id', 'in', invoice_ids)
            ])
            amount = self.env['account.payment']._compute_payment_amount(invoices, invoices[0].currency_id, self.journal_id, self.payment_date)
            # If amount is positive it is customer related else vendor related
            if amount > 0:
                customer_payment = True
            elif amount < 0:
                customer_payment = False
            else:
                raise UserError(_("Nothing to invoice!"))
            payments.custom_post(payment_amounts, customer_payment)
        else:
            payments.post()

        action_vals = {
            'name': _('Payments'),
            'domain': [('id', 'in', payments.ids), ('state', '=', 'posted')],
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(payments) == 1:
            action_vals.update({'res_id': payments[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals


class AccountPaymentRegisterLine(models.TransientModel):
    _name = 'account.payment.register.line'
    _description = 'Account Payment Register Line'

    account_payment_register_id = fields.Many2one('account.custom.payment.register', string='Register ID')
    move_id = fields.Many2one('account.move', string='Invoice/Bill', required=True)
    company_currency_id = fields.Many2one(related='account_payment_register_id.company_currency_id', string='Company Currency',
        readonly=True, store=True,
        help='Utility field to express amount currency')
    amount_total = fields.Monetary(string='Amount Total', compute='_compute_amount_total_residual', currency_field='company_currency_id')
    amount_residual = fields.Monetary(string='Amount Due', compute='_compute_amount_total_residual', currency_field='company_currency_id')
    amount_payment = fields.Monetary(string='Payment Amount', currency_field='company_currency_id')
    partner_id = fields.Many2one('res.partner', string='Partner', related='move_id.partner_id')
    
    @api.depends('move_id')
    def _compute_amount_total_residual(self):
        for record in self:
            if record.move_id:
                record.write({
                    'amount_total': record.move_id.amount_total,
                    'amount_residual': record.move_id.amount_residual
                })
            else:
                record.write({
                    'amount_total': 0.0,
                    'amount_residual': 0.0
                })

    @api.onchange('move_id')
    def _onchange_move_id(self):
        for record in self:
            if record.account_payment_register_id.partner_id and record.move_id:
                if record.partner_id != record.account_payment_register_id.partner_id:
                    raise UserError(_("You can't select invoices/bills with different partners!"))
            selected_move_ids = []
            for each_record in self.account_payment_register_id.register_line_ids:
                if each_record.move_id.id in selected_move_ids:
                    raise UserError(_("You can't select an invoice/bill multiple times!"))
                else:
                    selected_move_ids.append(each_record.move_id.id)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_custom_register_payment(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''
        move_ids = self.env['account.move'].search([
            ('id', 'in', active_ids)
        ])
        type = move_ids.mapped('type')
        if not (all(x == type[0] for x in type)):
            raise UserError(_("You can only select customer invoice or vendor bill at a time!"))
        context = self.env.context
        if move_ids[0].type == 'out_invoice':
            context['default_invoice_type'] = 'out_invoice'
        elif move_ids[0].type == 'in_invoice':
            context['default_invoice_type'] = 'in_invoice'
        context['default_company_id'] = self.env.company.id
        context['default_company_currency_id'] = self.env.company.currency_id.id
        return {
            'name': _('Multi-Invoice Payment'),
            'res_model': 'account.custom.payment.register',
            'view_mode': 'form',
            'view_id': self.env.ref('bi_multi_invoice_payment.view_account_custom_payment_form_multi').id,
            'context': context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
