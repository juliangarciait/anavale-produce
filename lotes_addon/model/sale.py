from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_lot_id = fields.Many2one('stock.production.lot', 'Lote', copy=False)
    x_lot_restante = fields.Float('Stock', related='x_lot_id.x_restante')

    # @api.multisss
    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        res['x_lot_id'] = self.x_lot_id.id
        return res

    @api.onchange('product_id')
    def _onchange_product_id_set_lot_domain(self):
        available_lot_ids = []
        if self.order_id.warehouse_id and self.product_id:
            location = self.order_id.warehouse_id.lot_stock_id
            quants = self.env['stock.quant'].read_group([
                ('product_id', '=', self.product_id.id),
                ('location_id', 'child_of', location.id),
                ('quantity', '>', 0),
                ('lot_id', '!=', False),
            ], ['lot_id'], 'lot_id')
            available_lot_ids = [quant['lot_id'][0] for quant in quants]
        self.x_lot_id = False
        return {
            'domain': {'x_lot_id': [('id', 'in', available_lot_ids)]}
        }

    @api.constrains('x_lot_id', 'product_id')
    def _check_stock(self):
        for record in self:
            if record.x_lot_id:
                restante = record.x_lot_id.x_restante
                if restante < self.product_uom_qty:
                    raise ValidationError(
                        'No existe suficiente cantidad en el lote, la cantidad maxima es: {} para el lote {}'.format(str(restante), record.x_lot_id.name))


