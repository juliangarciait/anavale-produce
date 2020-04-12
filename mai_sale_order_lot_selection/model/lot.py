from odoo import api, fields, models

class LotDatos(models.Model):
    _inherit = 'stock.production.lot'

    reservado = fields.Float(string='Reservado', compute="_compute_reservado", stored=True)
    restante = fields.Float(string='Queda', compute="_compute_restante", stored=True)

    @api.depends("product_id", "sale_order_ids", "quant_ids")
    def _compute_reservado(self):
        for record in self:
            quants = record.quant_ids.filtered(lambda q: q.location_id.usage in ['internal', 'transit'])
            record['reservado'] = sum(quants.mapped('reserved_quantity'))

    @api.depends("product_id", "reservado")
    def _compute_restante(self):
        for record in self:
            record['restante'] = record.product_qty - record.reservado