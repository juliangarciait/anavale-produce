# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import time 
from odoo.exceptions import ValidationError
import logging
import re

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'


    lot_reference = fields.Text('Lot Reference')

    def post(self):
         # OVERRIDE
         for invoice in self:
             for line in invoice.invoice_line_ids:
                 for sale_line in line.sale_line_ids:
                     line.lot_id = sale_line.lot_id
         res = super(AccountMove, self).post()
         return res

    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
         ''' Prepare values used to create the journal items (account.move.line) corresponding to the Cost of Good Sold
         lines (COGS) for customer invoices.
         Example:
         Buy a product having a cost of 9 being a storable product and having a perpetual valuation in FIFO.
         Sell this product at a price of 10. The customer invoice's journal entries looks like:
         Account                                     | Debit | Credit
         ---------------------------------------------------------------
         200000 Product Sales                        |       | 10.0
         ---------------------------------------------------------------
         101200 Account Receivable                   | 10.0  |
         ---------------------------------------------------------------
         This method computes values used to make two additional journal items:
         ---------------------------------------------------------------
         220000 Expenses                             | 9.0   |
         ---------------------------------------------------------------
         101130 Stock Interim Account (Delivered)    |       | 9.0
         ---------------------------------------------------------------
         Note: COGS are only generated for customer invoices except refund made to cancel an invoice.
         :return: A list of Python dictionary to be passed to env['account.move.line'].create.
         '''
         lines_vals_list = []
         for move in self:
             # Make the loop multi-company safe when accessing models like product.product
             move = move.with_context(force_company=move.company_id.id)

             if not move.is_sale_document(include_receipts=True) or not move.company_id.anglo_saxon_accounting:
                 continue

             for line in move.invoice_line_ids:

                 # Filter out lines being not eligible for COGS.
                 if line.product_id.type != 'product' or line.product_id.valuation != 'real_time':
                     continue

                 # Retrieve accounts needed to generate the COGS.
                 accounts = line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=move.fiscal_position_id)
                 debit_interim_account = accounts['stock_output']
                 credit_expense_account = accounts['expense']
                 if not credit_expense_account:
                     if move.type == 'out_refund':
                         credit_expense_account = move.journal_id.default_credit_account_id
                     else: # out_invoice/out_receipt
                         credit_expense_account = move.journal_id.default_debit_account_id
                 if not debit_interim_account or not credit_expense_account:
                     continue

                 # Compute accounting fields.
                 sign = -1 if move.type == 'out_refund' else 1
                 price_unit = line._stock_account_get_anglo_saxon_price_unit()
                 balance = sign * line.quantity * price_unit

                 # Add interim account line.
                 lines_vals_list.append({
                     'name': line.name[:64],
                     'move_id': move.id,
                     'partner_id': move.commercial_partner_id.id,
                     'product_id': line.product_id.id,
                     'product_uom_id': line.product_uom_id.id,
                     'quantity': line.quantity,
                     'price_unit': price_unit,
                     'debit': balance < 0.0 and -balance or 0.0,
                     'credit': balance > 0.0 and balance or 0.0,
                     'account_id': debit_interim_account.id,
                     'exclude_from_invoice_tab': True,
                     'is_anglo_saxon_line': True,
                     'lot_id': line.lot_id.id
                 })

                 # Add expense account line.
                 lines_vals_list.append({
                     'name': line.name[:64],
                     'move_id': move.id,
                     'partner_id': move.commercial_partner_id.id,
                     'product_id': line.product_id.id,
                     'product_uom_id': line.product_uom_id.id,
                     'quantity': line.quantity,
                     'price_unit': -price_unit,
                     'debit': balance > 0.0 and balance or 0.0,
                     'credit': balance < 0.0 and -balance or 0.0,
                     'account_id': credit_expense_account.id,
                     'analytic_account_id': line.analytic_account_id.id,
                     'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                     'exclude_from_invoice_tab': True,
                     'is_anglo_saxon_line': True,
                     'lot_id': line.lot_id.id
                 })
         return lines_vals_list

    @api.model
    def create(self, vals_list): 
        res = super(AccountMove, self).create(vals_list)

        res.lot_reference = ''
        try:
            purchase = self.env['purchase.order'].search([('invoice_ids', 'in', [res.id])])
            if purchase:    
                picking = self.env['stock.picking'].search([('purchase_id', '=', purchase.id), ('state', '=', 'done')], order='create_date desc', limit=1)
                move = self.env['stock.move.line'].search([('picking_id', '=', picking.id)], limit=1)
                reference = move.lot_id.name
                if reference and picking.date_done: 
                    reference = reference.split('-')

                    year = picking.date_done.strftime('%y')
                    if move.product_id.product_template_attribute_value_ids:
                        reference[1] = re.sub(str(move.product_id.product_template_attribute_value_ids[0].product_attribute_value_id.name), '', reference[1])

                    res.lot_reference = "{}{}-{}".format(res.partner_id.lot_code_prefix, year, reference[1]) 
        except:
            res.lot_reference = ''

        return res


    def _get_lot_reference(self): 
        self.lot_reference = ''
        purchase = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        if purchase:    
            picking = self.env['stock.picking'].search([('purchase_id', '=', purchase.id), ('state', '=', 'done')], order='create_date desc', limit=1)
            move = self.env['stock.move.line'].search([('picking_id', '=', picking.id)], limit=1)
            reference = move.lot_id.name
            if reference and picking.date_done: 
                reference = reference.split('-')

                year = picking.date_done.strftime('%y')
                if move.product_id.product_template_attribute_value_ids: 
                    reference[1] = re.sub(str(move.product_id.product_template_attribute_value_ids[0].product_attribute_value_id.name), '', reference[1])

                self.lot_reference = "{}{}-{}".format(self.partner_id.lot_code_prefix, year, reference[1]) 


    #@api.onchange('invoice_line_ids')
    #def onchange_invoice_line_ids(self):
    #    list_mapped = []
    #    for line in self.invoice_line_ids:
    #        if (line.product_id, line.lot_id) in list_mapped:
    #            raise ValidationError('Product {} with Lot {}! Already exist on the Invoice Lines. Please add amount in '
    #                            'existing line'.format(
    #                str(line.product_id.name), line.lot_id.name))
    #        list_mapped.append((line.product_id, line.lot_id))
