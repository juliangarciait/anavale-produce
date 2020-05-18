# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    lot_code_prefix = fields.Char('Lot Code', help='Code used to compute automatic Lot Numbers. 2 digits.', size=2)
    
    _sql_constraints = [
        ('lot_code_prefix_uniq', 'unique (lot_code_prefix)', "This Lot Code Prefix is already used in another Product!.")
    ]