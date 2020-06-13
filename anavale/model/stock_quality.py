# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import api, fields, models

class StockQualityCheck(models.Model):
    _name = 'stock.quality.check'
    _description = "Stock Quality Control"
    
    name = fields.Char('Name', readonly=True, compute='_compute_name', store=True)
    template_id = fields.Many2one('stock.quality.template', 'Template')  
    picking_id = fields.Many2one('stock.picking', 'Picking', readonly=True)  
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain="[('type', 'in', ['consu', 'product'])]")
    lot_id = fields.Many2one('stock.production.lot', 'Lot', domain="[('product_id', '=', product_id)]")    
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
    def _onchange_product_id(self):
        lot_ids = []
        for line in self.picking_id.move_line_ids_without_package.filtered(lambda q: q.product_id == self.product_id):
            lot_ids.append(line.lot_id.id)
        
        templates = self.env['stock.quality.template'].search([]).filtered(lambda t: t.default or self.product_id.id in t.product_ids.ids )
        
        return {
            'domain': {'lot_id': [('id', 'in', lot_ids)] ,
                       'template_id': [('id', 'in', templates.mapped('id'))] }
        }              
        
class StockQualityCheckLine(models.Model):
    _name = 'stock.quality.check.line'
    _description = "Stock Quality Control Line"
        
    quality_id = fields.Many2one('stock.quality.check', 'Quality Control Reference', index=True)  
    template_id = fields.Many2one('stock.quality.template', related="quality_id.template_id")  
    weight = fields.Float(string='Weight', digits='Product Unit of Measure', default=0.0)
    count = fields.Integer(string='Count')    
    point_ids = fields.One2many('stock.quality.check.point', 'line_id', string="Quality Points")
    size = fields.Selection([
        ('xl', 'XL'),
        ('jb', 'JB'),
        ('lg', 'LG')], string='Size')         

    def action_open_quality_points(self):
        """ Opens Quality Points.
        """
        view = self.env.ref('anavale.view_stock_quality_line_form')    
        return {
            'name': 'Stock Quality Points',
            'res_model':'stock.quality.check.line',
            'res_id': self.id,
            'views': [[view.id, "form"]],
            'view_mode': 'self',
            'type': 'ir.actions.act_window',
            'contex': dict(self.env.context),
            'target': 'new',
        }
        
class StockQualityCheckPoint(models.Model):
    _name = 'stock.quality.check.point'
    _description = "Stock Quality Control Check Points"
    
    def _get_point_id_domain(self):
        template_id = self.env.context.get('default_template_id', False)
        if template_id:
            template_rec = self.env['stock.quality.template'].browse(template_id)
            
            return [('id', 'in', template_rec.mapped('point_ids').mapped('id'))]
        return []
        
    line_id = fields.Many2one('stock.quality.check.line', 'Quality Line Reference')  
    point_id = fields.Many2one('stock.quality.point', string='Name', ondelete='restrict', required=True, domain=lambda self:self._get_point_id_domain())
    type = fields.Selection(related='point_id.type')
    value = fields.Char(' ', help="Value")
    value_boolean = fields.Boolean(' ', help="Selection if type Boolean")
    percentaje = fields.Percent(string='Percentaje')   
    help = fields.Char('Help', help="Type of value required for this quality point")
  
    @api.onchange('point_id')
    def _onchange_point_id(self):  
        if self.point_id.type == 'percentaje':
            self.help = 'Enter the number of ocurrences (integer), percentaje will be automatically calculated.'
        if self.point_id.type == 'integer':
            self.help = 'Enter the number of ocurrences (integer).'
        if self.point_id.type == 'float':
            self.help = 'Enter the a number.'
        if self.point_id.type == 'string':
            self.help = 'Enter the value.'
        if self.point_id.type == 'boolean':
            self.help = 'Toggle Yes/No the button.'
                   
    @api.onchange('value')
    def _onchange_picking_id(self):
        for record in self:
            value = record.value
            count = self.env.context.get('count', False)
            if record.type in ('integer', 'percentaje'):
                try:
                    value = int(value)
                except:
                    raise ValidationError("You have to enter an integer!")
                
            if record.type == 'float':
                try:
                    value = float(value)
                except:
                    raise ValidationError("You have to enter an integer or number with decimals!")
                    
            if record.type == 'integer' and count and value > count:
                raise ValidationError("Number must be less than or equal to %s" % count)
            
            elif value and record.type == 'percentaje' and record.line_id.count > 0:
                record.percentaje = int((value * 100) / record.line_id.count)
             