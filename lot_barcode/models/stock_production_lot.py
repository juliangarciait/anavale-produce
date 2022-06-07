# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class StockProductionLot(models.Model): 
    _inherit = 'stock.production.lot'

    packing = fields.Char('Packing')