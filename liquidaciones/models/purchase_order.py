# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _ 


class PurchaseOrder(models.Model): 
    _inherit = 'purchase.order'
    
    trouble_status = fields.Selection( selection=[("no", "No"), ("active", "Activo")],
        string="Trouble Status")
    
