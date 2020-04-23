from odoo import api, fields, models

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    sale_order_quantity = fields.Float(
        'Quantity in Sale Order', compute='_compute_sale_order_qty',
        help='Quantity of products in this quant in Sale Orders but not yet Reserved in a Stock Picking , in the default unit of measure of the product',
        store=True, readonly=True)
        
    available_quantity = fields.Float(
        'Quantity available for Sell', compute='_compute_sale_order_qty',
        help='Quantity of products in this quant avaiable for Sell including in-transit stock, in the default unit of measure of the product',
        store=True, readonly=True)
        
    def _compute_sale_order_qty(self):
        for quant in self.sudo():        
            domain = [('product_id', '=', quant.product_id.id),
                ('qty_to_deliver', '>', 0),
                ('order_id.state', '=', 'sale'),
                ('lot_id', '=', quant.lot_id.id)]
                
            quant.sale_order_quantity = 0    
            for so in self.env['sale.order.line'].search(domain):
                quant.sale_order_quantity += so.qty_to_deliver 
            quant.available_quantity = quant.quantity - quant.sale_order_quantity
            
    @api.model
    def _quant_tasks(self):
        res = super(StockQuant, self)._quant_tasks()
        self.sudo().search([])._compute_sale_order_qty()
        return res
