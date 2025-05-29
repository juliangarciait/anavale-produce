from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    quality_inspection_count = fields.Integer(compute='_compute_quality_inspection_count', string='Inspecciones de Calidad')

    def _compute_quality_inspection_count(self):
        for purchase in self:
            purchase.quality_inspection_count = self.env['quality.inspection'].search_count([('purchase_id', '=', purchase.id)])

    def action_view_quality_inspections(self):
        self.ensure_one()
        return {
            'name': 'Inspecciones de Calidad',
            'type': 'ir.actions.act_window',
            'res_model': 'quality.inspection',
            'view_mode': 'tree,form',
            'domain': [('purchase_id', '=', self.id)],
            'context': {'default_purchase_id': self.id},
        }