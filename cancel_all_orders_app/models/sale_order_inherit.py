# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class sale_order(models.Model):
    _inherit = 'sale.order'


    def action_cancel(self):
        for picking in self.picking_ids:
            if picking.state != 'cancel':
                picking.action_cancel()

        for invoice in self.invoice_ids :
            if invoice.state != 'cancel':
                invoice.button_draft()
                invoice.button_cancel()
                invoice.update({'name': '/'})
        res = super(sale_order, self).action_cancel()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: