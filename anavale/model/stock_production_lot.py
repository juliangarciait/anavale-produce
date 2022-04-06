# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StockProductionLot(models.Model):

    _inherit = 'stock.production.lot'
    _order = 'create_date DESC'