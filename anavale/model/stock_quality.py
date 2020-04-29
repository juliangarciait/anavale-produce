# -*- coding: utf-8 -*-
from odoo import api, fields, models

class StockQualityCheck(models.Model):
    _name = 'stock.quality.check'
    _description = "Stock Quality Control"
    
    name = fields.Char('Name', readonly=True, compute='_compute_name', store=True)
    picking_id = fields.Many2one('stock.picking', 'Picking', readonly=True)  
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain="[('type', 'in', ['consu', 'product'])]", required=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot', domain="[('product_id', '=', product_id)]", required=True)    
    responsible_id = fields.Char('Responsible')
    partner_id = fields.Many2one('res.partner', string='Vendor', readonly=True)
    quality_lines = fields.One2many('stock.quality.check.line', 'quality_id', string="Quality Lines", copy=False)
    notes = fields.Html('Notes')
    date = fields.Datetime(string='Date', required=True, copy=False, default=fields.Datetime.now, 
        help="Date when check was performed.")    
    
    @api.depends('picking_id', 'product_id', 'lot_id') 
    def _compute_name(self): 
        for record in self:
            record.name = '%s [%s/%s]' % (record.picking_id.name, record.product_id.name, record.lot_id.name)
                
    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        if not self.picking_id:
            return

        picking_id = self.picking_id
        order = self.env['purchase.order'].search([('name', '=', picking_id.origin)])
        if order and order.partner_id:
            self.partner_id = order.partner_id.id
        else:
            self.partner_id = False
        
        product_ids = []
        for line in self.picking_id.move_line_ids_without_package:
            product_ids.append(line.product_id.id)
        return {
            'domain': {'product_id': [('id', 'in', product_ids)] }
        }    
        
    @api.onchange('product_id')
    def _onchange_product_id_set_lot_domain(self):
        lot_ids = []
        for line in self.picking_id.move_line_ids_without_package.filtered(lambda q: q.product_id == self.product_id):
            lot_ids.append(line.lot_id.id)
            
        return {
            'domain': {'lot_id': [('id', 'in', lot_ids)] }
        }    
            
        # # Create Quality lines if necessary
        # quality_lines = []
        # from odoo.exceptions import UserError
        # # raise UserError('picking_id.move_line_ids_without_package [%s]' % picking_id.move_line_ids_without_package)
        # for line in picking_id.move_line_ids_without_package:
            # order_line_values = {
                # 'product_id': line.product_id.id,
                # 'lot_id': line.lot_id.id
            # }
            # quality_lines.append((0, 0, order_line_values))
        # self.quality_lines = quality_lines
        # raise UserError('quality_lines [%s]' % quality_lines)
        
class StockQualityCheckLine(models.Model):
    _name = 'stock.quality.check.line'
    _description = "Stock Quality Control Line"
    
    quality_id = fields.Many2one('stock.quality.check', 'Quality Control Reference', index=True)  
    weight = fields.Float(string='Weight', digits='Product Unit of Measure', default=0.0)
    count = fields.Integer(string='Count')    
    # size = fields.Selection([
        # ('xl', 'XL'),
        # ('jb', 'JB'),
        # ('lg', 'LG')], string='Size') 
    damage = fields.Percent(string='Damage (%)') 
    insect = fields.Percent(string='Insect (%)') 
    decay = fields.Percent(string='Decay (%)') 
    stripes = fields.Percent(string='Stripes (%)') 
    red = fields.Percent(string='Red (%)') 
    firmness = fields.Selection([
        ('1', 'Flacid'),
        ('2', 'Soft'),
        ('3', 'Firm'),
        ('4', 'Hard')], string='Firmness',)  
        
        
        
        
     # @api.onchange('picking_id')
    # def _onchange_picking_id(self):
        # if not self.picking_id:
            # return

        # picking_id = self.picking_id
        # if self.partner_id:
            # partner = self.partner_id
        # else:
            # partner = picking_id.partner_id
        # self.partner_id = partner.id
        # # Create Quality lines if necessary
        # quality_lines = []
        # from odoo.exceptions import UserError
        # # raise UserError('picking_id.move_line_ids_without_package [%s]' % picking_id.move_line_ids_without_package)
        # for line in picking_id.move_line_ids_without_package:
            # order_line_values = {
                # 'product_id': line.product_id.id,
                # 'lot_id': line.lot_id.id
            # }
            # quality_lines.append((0, 0, order_line_values))
        # self.quality_lines = quality_lines
        # raise UserError('quality_lines [%s]' % quality_lines)
        