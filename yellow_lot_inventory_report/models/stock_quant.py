# -*- coding: utf-8 -*-

from email.policy import default
from odoo import fields, models, api, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class StockQuant(models.Model): 
    _inherit = 'stock.quant'

    alert_date = fields.Datetime(related='lot_id.alert_date', store=True)

    current_date = fields.Datetime(compute='_get_current_date')

    def _get_current_date(self): 
        self.current_date = datetime.now()


