from odoo import api, fields, models


class LotData(models.Model):
    _inherit = 'stock.production.lot'

    parent_lod_id = fields.Many2one('stock.production.lot', string='Parent Lot',
                                    help="This field contains the information related to the Parent Lot if"
                                         "it is repack lot")

    child_lot_ids = fields.One2many('stock.production.lot', 'parent_lod_id',
                                    string="Child Lots")
