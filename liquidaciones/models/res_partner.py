# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _ 

porcentajes = [
    ('8', '8% comision'),
    ('9', '9% comision'),
    ('10', '10% comision'),
    ('11', '11% comision'),
    ('12', '12% comision'),

]
options_sel = [('si', 'SI'), ('no', 'NO')]


class ResPartner(models.Model): 
    _inherit = 'res.partner'

    price_type = fields.Selection([('fijo', 'Precio Fijo'), ('variable', 'Precio Variable')], string='Tipo de precio')
    commission_percentage = fields.Selection(porcentajes, string="% de Comision")
    freight_in = fields.Selection(options_sel, string="Flete de entrada?")
    mx_customs = fields.Selection(options_sel, string="Aduana MX?")
    us_customs = fields.Selection(options_sel, string="Aduana US?")
    in_and_out = fields.Selection(options_sel, string="In and Out?")
    box = fields.Selection(options_sel, string="Caja?")
    reference = fields.Char(string="Referencia")