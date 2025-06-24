# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class sale_order(models.Model):
    _inherit = 'sale.order'


    def action_cancel(self):
        for picking in self.picking_ids:
            if picking.custom_state_delivery in ['assigned', 'done']: 
                raise ValidationError (_('You cant cancel this sales order because it has a picking in state assigned or done'))
            if picking.state != 'cancel':
                if self.env.user.has_group('cancel_all_orders_app.group_cancel_sale_order_basic') and picking.state != 'done': 
                    picking.with_context(cancel_from_sale_order=True).action_cancel()
                    self.cancel_invoice()
                elif self.env.user.has_group('cancel_all_orders_app.group_cancel_sale_order_advanced'):
                    picking.with_context(cancel_from_sale_order=True).action_cancel()
                    self.cancel_invoice()
                else: 
                    raise ValidationError (_('You dont have the required permissions to cancel this sales order'))
            
        res = super(sale_order, self).action_cancel()
        return res

    def cancel_invoice(self): 
        for invoice in self.invoice_ids :
            if invoice.state != 'cancel':
                invoice.button_draft()
                invoice.button_cancel()
                invoice.update({'name': '/'})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: