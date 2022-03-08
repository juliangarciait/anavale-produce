# coding: utf-8

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockProductionLotTag(models.Model):
    _name = 'stock.production.lot.tag'

    name = fields.Char(string= 'nombre', required=True)
    lot_id = fields.One2many('stock.production.lot', 'id', string='Lot ID')