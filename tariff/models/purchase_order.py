# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import timedelta

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    importacion = fields.Selection([
        ('Si', 'Si'),
        ('No', 'No')
    ], string='Es Importacion?', required=True)

    entry_summary = fields.Char(string="Entry Summary", readonly=True)
