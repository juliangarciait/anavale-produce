# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)

class PrintLabels(models.TransientModel): 
    _name = 'print.labels'
    
    line_ids = fields.One2many('print.labels.line', 'print_label_id')
    
class PrintLabelsLine(models.TransientModel): 
    _name = 'print.labels.line'  
    
    product_id = fields.Many2one('product.product', string="Producto")
    lot_id = fields.Many2one('stock.production.lot')
    qty_pallet_boxes = fields.Char(string="Cajas Pallet")
    print_label_id = fields.Many2one('print.labels')
    
    def print_label(self): 
        self.ensure_one()
        self.lot_id.write({'packing' : self.qty_pallet_boxes})
        report_name = 'stock.label_lot_template_view'
        report_obj = self.env['ir.actions.report']._get_report_from_name(
            report_name)
        return report_obj.report_action(self.lot_id, data={})