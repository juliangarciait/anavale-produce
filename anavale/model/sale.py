from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def action_confirm(self):
        """ Method for 'Confirm' Button, makes sure
            lot still available before confirming."""
        res = super(SaleOrder, self).action_confirm()
        
        for line in self.mapped('order_line').filtered(lambda line: line.lot_id):
            res = line._get_lots(line.lot_id.id)
            if line.product_uom_qty > res['quantity']:
                raise UserError('Maximum %s units for selected Lot for Product %s!' % (res['quantity'], line.product_id.name))
        return res
        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_id = fields.Many2one('stock.production.lot', 'Lot', copy=False, required=True)
    lot_available_sell = fields.Float('Stock', readonly=1)

    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        res['lot_id'] = self.lot_id.id
        return res

    @api.onchange('product_uom_qty')
    def onchange_quantity(self):
        if self.product_id and self.lot_id and self.product_uom_qty > self.lot_available_sell:
            raise UserError('Maximum %s units for selected Lot!' % self.lot_available_sell)
            
    @api.onchange('product_id')
    def _onchange_product_id_set_lot_domain(self):
        lot_ids = []
        if self.order_id.warehouse_id and self.product_id:
            res = self._get_lots()
            lot_ids = res['lot_ids']  

        return {
            'domain': {'lot_id': [('id', 'in', lot_ids)],
                       'lot_available_sell': 0.0 }
        }    
        
    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        quantity = 0.0
        if self.lot_id:
            res = self._get_lots(self.lot_id.id)
            quantity = res['quantity']
            self.product_uom_qty = 0.0

        self.lot_available_sell = quantity
     
    def _get_lots(self, lot_id=False):
        """ Compute lot availability including real in-stock,
            plus on-transit minus so already confirmed but
            not yet delivered."""
        lot_ids = []        
        avail = {}
        quantity = 0.0        
        rounding = self.product_id.uom_id.rounding
        
        domain = [('product_id', '=', self.product_id.id), ('quantity', '>', 0)]
        so_domain = [('product_id', '=', self.product_id.id),
            ('qty_to_deliver', '>', 0),
            ('order_id.state', '=', 'sale')]
        if lot_id:
            domain += [('lot_id', '=', lot_id)]
            so_domain += [('lot_id', '=', lot_id)]
        else:
            domain += [('lot_id', '!=', False)]
            so_domain += [('lot_id', '!=', False)]
            
        # Quants already in stock
        for quant in self.env['stock.quant'].search(domain + [('location_id', 'child_of', self.order_id.warehouse_id.lot_stock_id.id)]):
            avail.setdefault(quant.lot_id.id, {'lot': quant.lot_id.id, 'qty': 0.0})
            avail[quant.lot_id.id]['qty'] += quant.quantity 
        
        # Quant in transit
        for quant in self.env['stock.quant'].search(domain + [('location_id', 'child_of', self.order_id.warehouse_id.wh_input_stock_loc_id.id)]):
            avail.setdefault(quant.lot_id.id, {'lot': quant.lot_id.id, 'qty': 0.0})
            avail[quant.lot_id.id]['qty'] += quant.quantity 
            
        # Quants in sale.order with stock.picking not yet assigned nor done (this quants are not yet reserved)
        for so in self.env['sale.order.line'].search(so_domain):
            avail.setdefault(so.lot_id.id, {'lot': so.lot_id.id, 'qty': 0.0})
            avail[so.lot_id.id]['qty'] -= so.qty_to_deliver 
         
        for lot in avail:
            if float_compare( avail[lot]['qty'], 0, precision_rounding=rounding) > 0:
               lot_ids.append(lot) 
               quantity += avail[lot]['qty']
        
        return {'lot_ids': lot_ids, 'quantity': quantity}