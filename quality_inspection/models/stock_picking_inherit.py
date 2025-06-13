from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    quality_inspect_count = fields.Integer(
        string='Quality Inspection Count',
        compute='_compute_quality_inspect_count',
        store=False
    )

    def _compute_quality_inspect_count(self):
        for picking in self:
            picking.quality_inspect_count = self.env['quality.inspect'].search_count([
                ('stock_picking_id', '=', picking.id)
            ])

    def action_open_quality_inspection(self):
        self.ensure_one()
        action = self.env.ref('quality_inspection.action_quality_inspect').read()[0]
        action['domain'] = [('stock_picking_id', '=', self.id)]
        action['context'] = {
            'default_stock_picking_id': self.id,
        }
        return action
