from odoo import models, fields

class Repack(models.Model):
    _inherit = 'repack.order'

    quality_inspect_count = fields.Integer(
        string='Quality Inspection Count',
        compute='_compute_quality_inspect_count',
        store=False
    )

    def _compute_quality_inspect_count(self):
        for repack in self:
            repack.quality_inspect_count = self.env['quality.inspect'].search_count([
                ('repack_order_id', '=', repack.id)
            ])

    def action_open_quality_inspection(self):
        self.ensure_one()
        action = self.env.ref('quality_inspection.action_quality_inspect').read()[0]
        action['domain'] = [('repack_id', '=', self.id)]
        action['context'] = {
            'default_repack_order_id': self.id,
        }
        return action