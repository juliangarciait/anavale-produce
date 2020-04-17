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

from odoo import api, fields, models, _


class ActionViewPickings(models.TransientModel):

    _name = 'view.picking.product'
    _description = "View Picking Products"

    quant_id = fields.Many2one('stock.quant', string="Quant")
    product_id = fields.Many2one(
        'product.product', string='Product', related='quant_id.product_id')
    inventory_quantity = fields.Float(
        string='On Hand Quantity', related='quant_id.inventory_quantity')
    reserved_quantity = fields.Float(
        string='Reserved Quantity', related="quant_id.reserved_quantity")
    qty_to_sale = fields.Float(
        string='Quantity To Sale', related="quant_id.qty_to_sale")
    incoming_qty = fields.Float(
        string='Incoming Quantity', related="quant_id.incoming_qty")
    location_id = fields.Many2one(
        'stock.location', string='Location', related="quant_id.location_id")
    line_ids = fields.One2many(
        'view.picking.line', 'wizard_id', string='View Lines')
    mode = fields.Selection([('picking', 'Picking'), ('reserved', 'Reserved')], default='picking')

    @api.model
    def default_get(self, fields):
        res = super(ActionViewPickings, self).default_get(fields)
        if self._context.get('default_quant_id'):
            quant = self.env['stock.quant'].sudo().browse(
                self._context.get('default_quant_id'))

            if self._context.get('default_mode') == 'picking':
                picking_ids = []
                pickings = self.env['stock.picking'].sudo().search([('picking_type_code', '=', 'incoming'), (
                    'location_dest_id', '=', quant.location_id.id), ('state', '=', 'assigned')])
                line_vals = []
                for picking in pickings:
                    for move in picking.move_ids_without_package:
                        if move.product_id.id == quant.product_id.id:
                            picking_ids.append(picking.id)
                            line_vals.append((0, 0, {
                                'move_id': move.id,
                                'picking_id': picking.id,
                                'product_uom_qty': move.product_uom_qty,
                                'quantity_done': move.quantity_done,
                                'scheduled_date': picking.scheduled_date,
                            }))
                res['line_ids'] = line_vals
        return res


class ViewLines(models.TransientModel):

    _name = 'view.picking.line'
    _description = 'View Picking Lines'

    wizard_id = fields.Many2one('view.picking.product', string='Wizard')
    move_id = fields.Many2one('stock.move', string="Move")
    picking_id = fields.Many2one('stock.picking', string='Receipt', related="move_id.picking_id")
    product_uom_qty = fields.Float(
        string='Demand (Incoming)', related="move_id.product_uom_qty")
    quantity_done = fields.Float(
        string='Done', related="move_id.quantity_done")
    scheduled_date = fields.Datetime(string='Incoming Date', related="move_id.date_expected")
