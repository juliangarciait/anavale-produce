from odoo import api, fields, models

class QualityInspection(models.Model):
    _name = 'quality.inspection'
    _description = 'Inspección de Calidad'

    purchase_id = fields.Many2one('purchase.order', string='Orden de Compra', required=True, readonly=True)
    picking_id = fields.Many2one('stock.picking', string='Albarán de Recepción', required=True, readonly=True)
    inspector_id = fields.Many2one('res.users', string='Inspector', default=lambda self: self.env.user)
    inspection_date = fields.Datetime(string='Fecha de Inspección', default=fields.Datetime.now)
    inspection_report = fields.Char(string='Reporte de Inspección (Enlace)')
    inspection_lines = fields.One2many('quality.inspection.line', 'inspection_id', string='Líneas de Inspección')


class QualityInspectionLine(models.Model):
    _name = 'quality.inspection.line'
    _description = 'Línea de Inspección de Calidad'

    inspection_id = fields.Many2one('quality.inspection', string='Inspección', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    pieces_per_box = fields.Integer(string='Piezas por Caja')
    defective_pieces = fields.Integer(string='Piezas con Defecto')
    defect_percentage = fields.Float(string='% de Defectos', compute='_compute_defect_percentage', store=True)
    product_report = fields.Char(string='Reporte de Inspección del Producto (Enlace)')

    @api.depends('pieces_per_box', 'defective_pieces')
    def _compute_defect_percentage(self):
        for line in self:
            if line.pieces_per_box:
                line.defect_percentage = (line.defective_pieces / line.pieces_per_box) * 100
            else:
                line.defect_percentage = 0.0