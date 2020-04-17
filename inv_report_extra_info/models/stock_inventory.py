# -*- coding: utf-8 -*-
###################################################################################
#
#    ITStore
#    Copyright (C) 2019-TODAY ITStore (<http://itstore.odoo.com>).
#    Author: ITStore (<http://itstore.odoo.com>)
#
#    you can modify it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#
###################################################################################

from odoo import fields, models, api


class StockQuant(models.Model):

    _inherit = 'stock.quant'

    def _compute_qty_to_sale(self):
        for quant in self.sudo():
            qty = quant.inventory_quantity - quant.reserved_quantity
            if qty > 0:
                quant.qty_to_sale = qty
                quant.qty_to_sale_store = qty
            else:
                quant.qty_to_sale = 0
                quant.qty_to_sale_store = 0

    def _compute_incoming_qty(self):
        for quant in self.sudo():
            pickings = self.env['stock.picking'].sudo().search([('picking_type_code', '=', 'incoming'), ('location_dest_id', '=', quant.location_id.id), ('state', 'not in', ['draft', 'done', 'cancel'])])
            qty = 0
            for picking in pickings:
                for move in picking.move_ids_without_package:
                    if move.product_id.id == quant.product_id.id:
                        qty += move.product_uom_qty
            quant.incoming_qty = qty
            quant.incoming_qty_store = qty

    qty_to_sale = fields.Float(
        string='Available Quantity', compute='_compute_qty_to_sale')
    incoming_qty = fields.Float(
        string='Ordered Incoming', compute="_compute_incoming_qty")
    qty_to_sale_store = fields.Float(
        string='Available Quantity')
    incoming_qty_store = fields.Float(
        string='Ordered Incoming')

    def action_view_pickings(self):
        self.ensure_one()
        return {
            'name': "Ordered Incoming Stock",
            'type': 'ir.actions.act_window',
            'res_model': 'view.picking.product',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'context': {'default_quant_id': self.id, 'default_mode': 'picking'},
            'target': 'new',
        }
