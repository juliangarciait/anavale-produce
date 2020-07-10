# -*- coding: utf-8 -*-

from odoo import api, fields, models

class StockQualityPoint(models.Model):
    _name = 'stock.quality.point'
    _description = "Stock Quality Control Points"
    _order = 'sequence,name,id'  
        
    @api.model
    def _default_sequence_id(self):
        rec = self.search([], order="sequence desc", limit=1)
        return rec.sequence + 10 if rec else 10
        
    name = fields.Char('Name',required=True)
    sequence = fields.Integer(default=_default_sequence_id, help="Sequence")  
    type = fields.Selection([
        ('percentaje', 'Percentaje'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('string', 'String'),
        ('boolean', 'Boolean')], default='percentaje', required=True, help="What kind of Quality Point this is?.")
        
    def _report_format_value(self, point):
        """ Format value for PDF report"""
        
        if self.type == 'percentaje':
            percentaje = float(point.percentaje) / 100
            value = "{:.2%}".format(percentaje)
            
        elif self.type in ('integer', 'string'):
            value = point.value
            
        elif self.type == 'float':
            value = "{:.2f}".format(point.value)
                        
        elif self.type == 'boolean':
            value = 'Yes' if point.value_boolean else 'No'
            
        return value


        