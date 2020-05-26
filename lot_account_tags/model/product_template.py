# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    analytic_account_id = fields.Many2one('account.analytic.account', string='Accounting Analytics',
                                     help="This field contains the information related to the account analytics",
                                     copy=False)
    