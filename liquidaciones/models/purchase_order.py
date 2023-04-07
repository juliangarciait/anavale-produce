# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _ 


class PurchaseOrder(models.Model): 
    _inherit = 'purchase.order'
    
    trouble_status = fields.Selection( selection=[("no", "No"), ("active", "Activo")],
        string="Trouble Status")
    
    price_type = fields.Integer(string='Tipo de precio')
    commission_percentage = fields.Integer(string='% de Comisión')
    freight_in = fields.Integer(string="Flete de entrada?")
    mx_customs = fields.Integer(string="Aduana MX?")
    us_customs = fields.Integer(string="Aduana US?")
    in_and_out = fields.Integer(string="In and Out?")
    box = fields.Integer(string="Caja?")
    reference = fields.Integer(string="Referencia")