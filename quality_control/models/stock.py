from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    purchase_id = fields.Many2one('purchase.order', string='Orden de Compra', related='move_lines.purchase_line_id.order_id', store=True)

    def action_create_quality_inspection(self):
        self.ensure_one()
        # Verificar si ya existe una inspección para este picking
        existing_inspection = self.env['quality.inspection'].search([('picking_id', '=', self.id)])
        if existing_inspection:
            return {
                'name': 'Inspección de Calidad Existente',
                'type': 'ir.actions.act_window',
                'res_model': 'quality.inspection',
                'view_mode': 'form',
                'res_id': existing_inspection.id,
                'target': 'current',
            }
        else:
            # Crear una nueva inspección
            inspection = self.env['quality.inspection'].create({
                'picking_id': self.id,
                'purchase_id': self.purchase_id.id,  # Asumiendo que hay un campo purchase_id en stock.picking
            })
            return {
                'name': 'Nueva Inspección de Calidad',
                'type': 'ir.actions.act_window',
                'res_model': 'quality.inspection',
                'view_mode': 'form',
                'res_id': inspection.id,
                'target': 'current',
            }