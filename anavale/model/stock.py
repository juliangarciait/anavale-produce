from odoo import api, fields, models
from odoo.exceptions import UserError

class Picking(models.Model):
    _inherit = "stock.picking"
    
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

    def write(self,vals):
        res = super(StockMove, self).write(vals)
        for rec in self:
            if rec.sale_line_id and rec.picking_id and rec.lot_id and rec.move_line_ids and sum(rec.move_line_ids.mapped('qty_done')) == 0.0:
                for line in rec.move_line_ids:
                    line.lot_id = rec.lot_id.id
                    line.qty_done = rec.product_uom_qty
        return res
