# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

class SaleOrder(models.Model): 
    _inherit = 'sale.order'

    def action_confirm(self): 
        today = datetime.now().date()
        inv_ids = self.env['account.move'].search([('partner_id', '=', self.partner_id.id), ('state', '=', 'posted'), ('invoice_payment_state', '=', 'not_paid'), ('type', '=', 'out_invoice'), ('invoice_date_due', '<', today)])
        if inv_ids and not self.partner_id.over_credit:
            raise ValidationError (_("You can not confirm sale order for this Customer. This customer has one or more overdue invoices."))
        return super(SaleOrder, self).action_confirm()
