# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    over_credit = fields.Boolean('Allow Over Credit?')
    credit_insured = fields.Float(string='Asegurado')
    credit_manual = fields.Float(string='Manual')
    credit_available = fields.Float(string='Credit Available',compute='_compute_credit_available', store=True)
    credit_limit = fields.Float(string='Credit Limit', compute='_compute_credit_limit', store=True)

    @api.onchange('over_credit')
    def onchange_over_credit(self):
        for rec in self:
            msg = ""
            if rec.over_credit:
                msg = "Over credit activado\n"
                rec._origin.message_post(body=msg)

    @api.depends('credit_insured', 'credit_manual')
    def _compute_credit_limit(self):
        for rec in self:
            rec.credit_limit = rec.credit_insured + rec.credit_manual

    @api.onchange('credit_insured', 'credit_manual')
    def onchange_credito(self):
        for rec in self:
            credit_insured_ant = rec._origin.credit_insured
            credit_manual_ant = rec._origin.credit_manual
            msg = ""
            if credit_insured_ant != rec.credit_insured:
                msg = "· Credito Asegurado cambio de {} a {}\n".format(credit_insured_ant, rec.credit_insured)
            if credit_manual_ant != rec.credit_manual:
                msg += "· Credito Manual cambio de {} a {}\n".format(credit_manual_ant, rec.credit_manual)
            rec._origin.message_post(body=msg)
            # rec.credit_limit = rec.credit_insured
            # if rec.credit_manual > rec.credit_insured:
            #     rec.credit_limit = rec.credit_manual

    @api.depends('credit_limit')
    def _compute_credit_available(self):
        #self.ensure_one()
        for rec in self:
            partner = rec
            user_id = rec.env['res.users'].sudo().search([
                ('partner_id', '=', partner.id)], limit=1)
            if user_id and not user_id.has_group('base.group_portal') or not \
                    user_id:
                moveline_obj = rec.env['account.move'].sudo()
                movelines = moveline_obj.search(
                    [('partner_id', '=', partner.id),
                     ('state', '=', 'posted'),
                     ('type', '=', 'out_invoice')]
                )
                confirm_sale_order = rec.env['sale.order'].sudo().search([('partner_id', '=', rec.id),
                                                  ('invoice_status', '=', 'to invoice')])
                confirm_sale_order_delivery = rec.env['sale.order'].sudo().search([('partner_id', '=', partner.id),
                                                  ('custom_state_delivery', '=', 'Waiting')])
                debit, credit = 0.0, 0.0
                due = 0
                amount_total = 0.0
                for status in confirm_sale_order:
                    amount_total += status.amount_total
                for status in confirm_sale_order_delivery:
                    amount_total += status.amount_total
                # rec.credit_limit = rec.credit_insured
                rec.credit_limit = rec.credit_insured + rec.credit_manual
                # if rec.credit_manual > rec.credit_insured:
                #     rec.credit_limit = rec.credit_manual
                for line in movelines:
                    due += line.amount_residual_signed
                rec.credit_available = rec.credit_limit - due - amount_total



