# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockProductionLot(models.Model):

    _inherit = 'stock.production.lot'
    _order = 'create_date DESC'


    available_to_choose = fields.Boolean('Available', store=True, compute='_available')

    @api.depends('quant_ids', 'quant_ids.reserved_quantity', 'quant_ids.quantity', 'product_qty')
    def _available(self):
        for lot in self:
            if lot.product_qty <= 0:
                lot.available_to_choose = False
            elif lot.product_qty > 0:
                quants = lot.quant_ids.filtered(lambda q: q.location_id.usage in ['internal', 'transit'])
                for q in quants:
                    if q.quantity - q.reserved_quantity > 0:
                        lot.available_to_choose = True
                    elif q.quantity - q.reserved_quantity < 0:
                        lot.available_to_choose = False

    @api.onchange('product_qty')
    def _onchange_usage(self):
        if self.product_qty > 0:
            self.available_to_choose = True
        else:
            self.available_to_choose = False

    def _product_qty(self):
        res = super(StockProductionLot, self)._product_qty()
        for lot in self:
            if lot.product_qty > 0:
                lot.available_to_choose = True
