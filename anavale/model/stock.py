# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class Picking(models.Model):
    _inherit = "stock.picking"
    
    quality_ids = fields.One2many('stock.quality.check', 'picking_id', 'Checks')
    quality_count = fields.Integer(compute='_compute_quality_count')
    quality_check_todo = fields.Boolean('Pending checks', compute='_compute_quality_check_todo')
        
    def _compute_quality_count(self):
        for picking in self:
            picking.quality_count = len(picking.quality_ids)
            
    def _compute_quality_check_todo(self):
        for record in self:
            order = self.env['purchase.order'].search([('name', '=', record.origin)])
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', record.company_id.id)], limit=1)
            if warehouse and order and record.picking_type_id.code == 'internal' and record.location_dest_id == warehouse.lot_stock_id:
                record.quality_check_todo = True
            else:
                record.quality_check_todo = False
        
    # def open_quality_check(self):
        # """ Boton 'Quality Checks' """
        # self.ensure_one()
        
        # action = self.env.ref('anavale.stock_quality_check_action').read()[0]
        # action['context'] = dict(self._context, default_picking_id=self.id)
        # if self.quality_count == 0:
            # action['view_mode'] = 'form,tree'
            # action['view_id'] = self.env.ref('anavale.stock_quality_check_view_form').id
        # else:
            # action['view_id'] = self.env.ref('anavale.stock_quality_check_view_tree').id
            # # action['res_id'] = self.quality_ids
            # action['domain'] = [('id', 'in', self.quality_ids)]
        # return action

    def action_assign(self):
        res = super(Picking, self).action_assign()
        moves = self.mapped('move_lines').filtered(lambda move: move.lot_id)
        if self.picking_type_id.code == 'outgoing' and moves:
            for ml in moves.mapped('move_line_ids'):
                if ml.product_id == ml.move_id.product_id and ml.lot_id != ml.move_id.lot_id:
                    raise UserError('Only same %s Lot allowed to deliver for product %s!' % (ml.move_id.lot_id.name, ml.product_id.name))        
        return res      
 
class StockMove(models.Model):
    _inherit = 'stock.move'

    lot_id = fields.Many2one('stock.production.lot', string="Crate", copy=False)

    @api.model
    def create(self, vals):
        if vals.get('sale_line_id'):
            sale_line_id = self.env['sale.order.line'].browse(vals['sale_line_id'])
            if sale_line_id and sale_line_id.lot_id:
                vals.update({'lot_id': sale_line_id.lot_id.id})
        return super(StockMove, self).create(vals)

    # def write(self,vals):
        # res = super(StockMove, self).write(vals)
        # for rec in self:
            # if rec.sale_line_id and rec.picking_id and rec.lot_id and rec.move_line_ids and sum(rec.move_line_ids.mapped('qty_done')) == 0.0:
                # for line in rec.move_line_ids:
                    # line.lot_id = rec.lot_id.id
                    # line.qty_done = line.product_uom_qty #rec.product_uom_qty
        # return res

    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        if self._context.get("sol_lot_id"):
            lot_id = self.sale_line_id.lot_id
        return super()._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        if reserved_quant and self.sale_line_id:
            vals["lot_id"] = self.sale_line_id.lot_id.id
        return vals
        
        
    def _action_assign(self):
        raise UserError("FILTERED %s" % self.filtered(lambda m: m.state in ['confirmed', 'waiting', 'partially_available']))
    
        res = super(StockMove, self)._action_assign()
        
        return res