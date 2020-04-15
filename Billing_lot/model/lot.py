from odoo import api, fields, models

class LotDatos(models.Model):
    _inherit = 'stock.production.lot'

    ExtBills = fields.One2many('account.move', 'LotId', help='bill en este lote')

