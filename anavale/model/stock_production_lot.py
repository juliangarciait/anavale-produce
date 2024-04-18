# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockProductionLot(models.Model):

    _inherit = 'stock.production.lot'
    _order = 'create_date DESC'


    available_to_choose = fields.Boolean('Available', store=True)

    @api.depends('quant_ids', 'quant_ids.reserved_quantity', 'quant_ids.quantity', 'product_qty')
    def _available(self):
        for lot in self:
            if lot.product_qty <= 0:
                lot.available_to_choose = False
            else:
                lot.available_to_choose = True

    def _product_qty(self):
        res = super(StockProductionLot, self)._product_qty()
        for lot in self:
            if lot.product_qty > 0:
                lot.available_to_choose = True
            else: 
                lot.available_to_choose = False

    def create(self, vals):
        res = super(StockProductionLot, self).create(vals)
        for lot in res:
            lot.available_to_choose = True
        return res

