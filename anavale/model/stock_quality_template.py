# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import api, fields, models

class StockQualityTemplate(models.Model):
    _name = 'stock.quality.template'
    _description = "Stock Quality Control Template"
        
    name = fields.Char('Name',required=True)
    point_ids = fields.Many2many('stock.quality.point', string='Quality Checks',  
        domain="[('type', '!=', 'service')]", required=True)
    product_ids = fields.Many2many('product.product', string='Productos',  
        domain="[('type', '!=', 'service')]")
    default = fields.Boolean('Default Template', default=False,
        help="Template to be used when the product is not assigned to any specific template")
                
    @api.constrains('default')   
    def _validate_default(self):
        for record in self:
            if len(record.product_ids) > 0 and record.default:
                raise ValidationError("Default Template can not have Products assigned")
                
            if not record.default and len(record.product_ids) <= 0:
                raise ValidationError("Add Products to this Template")
                
            default_template = self.search([('id', '!=', record.id),('default', '=', True)], limit=1)
            if record.default and default_template:
                raise ValidationError("Template %s is already the default Template, make that template no default and try again" % default_template.name)
                