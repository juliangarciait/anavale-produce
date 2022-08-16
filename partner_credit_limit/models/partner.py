# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    over_credit = fields.Boolean('Allow Over Credit?')
    credit_insured = fields.Float(string='Asegurado')
    credit_manual = fields.Float(string='Manual')
    credit_available = fields.Float(string='Credit Available',compute='_compute_credit_available')

    @api.onchange('credit_insured', 'credit_manual')
    def onchange_credito(self):
        self.credit_limit = self.credit_insured
        if self.credit_manual > self.credit_insured:
            self.credit_limit = self.credit_manual

    def _compute_credit_available(self):
        self.ensure_one()
        partner = self
        user_id = self.env['res.users'].sudo().search([
            ('partner_id', '=', partner.id)], limit=1)
        if user_id and not user_id.has_group('base.group_portal') or not \
                user_id:
            moveline_obj = self.env['account.move'].sudo()
            movelines = moveline_obj.search(
                [('partner_id', '=', partner.id),
                 ('state', '=', 'posted'),
                 ('type', '=', 'out_invoice')]
            )
            confirm_sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', self.id),
                                              ('invoice_status', '=', 'to invoice')])
            confirm_sale_order_delivery = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id),
                                              ('custom_state_delivery', '=', 'Waiting')])
            debit, credit = 0.0, 0.0
            due = 0
            amount_total = 0.0
            for status in confirm_sale_order:
                amount_total += status.amount_total
            for status in confirm_sale_order_delivery:
                amount_total += status.amount_total
            self.credit_limit = self.credit_insured
            if self.credit_manual > self.credit_insured:
                self.credit_limit = self.credit_manual
            for line in movelines:
                due += line.amount_residual_signed
            self.credit_available = self.credit_limit - due - amount_total



