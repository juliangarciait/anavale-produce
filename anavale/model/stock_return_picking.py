# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def default_get(self, fields):
        """Sobrescribir para cargar automáticamente los lotes"""
        res = super(StockReturnPicking, self).default_get(fields)
        
        if res.get('product_return_moves'):
            # Actualizar las líneas existentes con información del lote
            for line_vals in res['product_return_moves']:
                if isinstance(line_vals, dict) and line_vals.get('move_id'):
                    move = self.env['stock.move'].browse(line_vals['move_id'])
                    # Buscar el lote en las líneas de movimiento completadas
                    if move.move_line_ids:
                        # Tomar el primer lote de las líneas de movimiento con qty_done > 0
                        move_line_with_lot = move.move_line_ids.filtered(lambda ml: ml.lot_id and ml.qty_done > 0)
                        if move_line_with_lot:
                            line_vals['lot_id'] = move_line_with_lot[0].lot_id.id
                        elif move.move_line_ids[0].lot_id:
                            # Si no hay qty_done, tomar el primer lote disponible
                            line_vals['lot_id'] = move.move_line_ids[0].lot_id.id
                    # Fallback: si el movimiento tiene lot_id directamente
                    elif move.lot_id:
                        line_vals['lot_id'] = move.lot_id.id
        
        return res
    
    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        res = super(StockReturnPicking, self)._prepare_stock_return_picking_line_vals_from_move(stock_move)
        res['lot_id'] = stock_move.lot_id.id
        return res
        # quantity = stock_move.product_qty - sum(
        #     stock_move.move_dest_ids
        #     .filtered(lambda m: m.state in ['partially_available', 'assigned', 'done'])
        #     .mapped('move_line_ids.product_qty')
        # )
        # quantity = float_round(quantity, precision_rounding=stock_move.product_uom.rounding)
        # return {
        #     'product_id': stock_move.product_id.id,
        #     'quantity': quantity,
        #     'move_id': stock_move.id,
        #     'uom_id': stock_move.product_id.uom_id.id,
        #     'lot_id': stock_move.lot_id.id
        # }

    def create_returns(self):
        """Sobrescribir para crear las líneas de movimiento con lotes"""
        # Ejecutar la lógica estándar del wizard
        result = super(StockReturnPicking, self).create_returns()
        
        # Obtener el picking creado
        if result and result.get('res_id'):
            return_picking = self.env['stock.picking'].browse(result['res_id'])
            
            # Crear las líneas de movimiento con información del lote
            for move in return_picking.move_lines:
                # Solo crear líneas si no existen ya
                if move.lot_id and not move.move_line_ids:
                    # Crear línea de movimiento con el lote
                    move_line_vals = {
                        'move_id': move.id,
                        'product_id': move.product_id.id,
                        'product_uom_id': move.product_uom.id,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.location_dest_id.id,
                        'lot_id': move.lot_id.id,
                        'qty_done': move.product_uom_qty,
                        'product_uom_qty': move.product_uom_qty,
                        'picking_id': return_picking.id,
                    }
                    self.env['stock.move.line'].create(move_line_vals)
                    return_picking.action_assign()
                    return_picking.write({'create_lot_name': False})
                # Si ya existen líneas pero no tienen lote, actualizarlas
                elif move.lot_id and move.move_line_ids:
                    for move_line in move.move_line_ids:
                        if not move_line.lot_id:
                            move_line.write({
                                'lot_id': move.lot_id.id,
                                'qty_done': move_line.product_uom_qty,
                            })
                    return_picking.action_assign()
                    return_picking.write({'create_lot_name': False})

        
        return result


class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    lot_id = fields.Many2one(
        'stock.production.lot', 
        string='Lot/Serial Number',
        help='Lot/Serial number from the original movement'
    )

    @api.onchange('move_id')
    def _onchange_move_id(self):
        """Cuando cambia el movimiento, actualizar el lote"""
        if self.move_id:
            # Buscar en las líneas de movimiento
            if self.move_id.move_line_ids:
                move_line_with_lot = self.move_id.move_line_ids.filtered(lambda ml: ml.lot_id and ml.qty_done > 0)
                if move_line_with_lot:
                    self.lot_id = move_line_with_lot[0].lot_id.id
                elif self.move_id.move_line_ids[0].lot_id:
                    self.lot_id = self.move_id.move_line_ids[0].lot_id.id
                else:
                    self.lot_id = False
            # Fallback: buscar en el movimiento principal
            elif self.move_id.lot_id:
                self.lot_id = self.move_id.lot_id.id
            else:
                self.lot_id = False
        else:
            self.lot_id = False

    def _prepare_move_default_values(self, return_line, new_picking):
        """Sobrescribir para incluir el lote en el movimiento de devolución"""
        vals = super(StockReturnPickingLine, self)._prepare_move_default_values(return_line, new_picking)
        
        # Agregar el lote al movimiento de devolución
        if return_line.lot_id:
            vals['lot_id'] = return_line.lot_id.id
            
        return vals

    @api.model
    def create(self, vals):
        """Cuando se crea una línea, cargar automáticamente el lote del movimiento original"""
        res = super(StockReturnPickingLine, self).create(vals) 
        res.lot_id = self.env['stock.move'].browse(vals['move_id']).lot_id.id
        # if vals.get('move_id') and not vals.get('lot_id'):
        #     move = self.env['stock.move'].browse(vals['move_id'])
        #     # Buscar en las líneas de movimiento
        #     if move.move_line_ids:
        #         move_line_with_lot = move.move_line_ids.filtered(lambda ml: ml.lot_id and ml.qty_done > 0)
        #         if move_line_with_lot:
        #             vals['lot_id'] = move_line_with_lot[0].lot_id.id
        #         elif move.move_line_ids[0].lot_id:
        #             vals['lot_id'] = move.move_line_ids[0].lot_id.id
        #     # Fallback: buscar en el movimiento principal
        #     elif move.lot_id:
        #         vals['lot_id'] = move.lot_id.id
        return res