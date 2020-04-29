# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    def button_cancel(self):
        for order in self:

            for picking in order.picking_ids:
                if picking.state != 'cancel':
                    picking.cancel_stock_picking()

            for invoice in order.invoice_ids :
                if invoice.state != 'cancel':
                    invoice.button_draft()
                    invoice.button_cancel()
                    invoice.update({'name': '/'})

        self.update({'state': 'cancel'})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: