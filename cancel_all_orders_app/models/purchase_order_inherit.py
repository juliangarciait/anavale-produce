# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from dateutil import relativedelta
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_cancel(self):
        for order in self:
            if self._context.get('button_cancel') == True:
                for pick in order.picking_ids.filtered(lambda r: r.state != 'cancel'):
                    pick.with_context(action_cancel=True).action_cancel()

                for invoice in order.invoice_ids :
                    if invoice.state != 'cancel':
                        invoice.button_draft()
                        invoice.button_cancel()
                        invoice.update({'name': '/'})
                order.update({'state': 'cancel'})
            else:
                for move in order.order_line.mapped('move_ids'):
                    if move.state == 'done':
                        raise UserError(_('Unable to cancel purchase order %s as some receptions have already been done.') % (order.name))
                # If the product is MTO, change the procure_method of the the closest move to purchase to MTS.
                # The purpose is to link the po that the user will manually generate to the existing moves's chain.
                if order.state in ('draft', 'sent', 'to approve', 'purchase'):
                    for order_line in order.order_line:
                        order_line.move_ids._action_cancel()
                        if order_line.move_dest_ids:
                            move_dest_ids = order_line.move_dest_ids
                            if order_line.propagate_cancel:
                                move_dest_ids._action_cancel()
                            else:
                                move_dest_ids.write({'procure_method': 'make_to_stock'})
                                move_dest_ids._recompute_state()

                for pick in order.picking_ids.filtered(lambda r: r.state != 'cancel'):
                    pick.action_cancel()
                order.order_line.write({'move_dest_ids':[(5,0,0)]})
                return super(PurchaseOrder, self).button_cancel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: