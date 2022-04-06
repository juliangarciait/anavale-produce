# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    lot_id = fields.Many2one('stock.production.lot', string='Lot')

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        if self.lot_id:
            self.name = self.lot_id.name
            self.analytic_tag_ids = self.lot_id.analytic_tag_ids