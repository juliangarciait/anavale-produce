from odoo import api, fields, models


class BillLot(models.Model):
    _inherit = 'account.move'

    LotId = fields.Selection(related='stock.production.lot', string="Asignar a Lote", store=True)

