# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    lot_code_prefix = fields.Char('Lot Code', help='Code used to compute automatic Lot Numbers. 4 digits.', size=4)
    account_tag_id = fields.Many2one('account.analytic.tag', string='Accounting Tag',
                                     help="This field contains the information related to the account tag for this "
                                          "product",
                                     copy=False)
    
    _sql_constraints = [
        ('lot_code_prefix_uniq', 'unique (lot_code_prefix)', "This Lot Code Prefix is already used in another Product!.")
    ]