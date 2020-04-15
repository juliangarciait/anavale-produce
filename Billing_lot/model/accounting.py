from odoo import api, fields, models


class BillLot(models.Model):
    _inherit = 'account.move'

    LotId = fields.Many2one('stock.production.lot', string="Asignar a Lote", store=True)

