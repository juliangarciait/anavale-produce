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

SiNo = [
    ('si','SI'),
    ('no','NO'),
]

Flete_opciones = [
    ('si','Se paga y se descuenta'),
    ('no','Se paga, NO se descuenta'),
    ('nono','No se paga')
]

InOut_opciones = [
    ('si','SI se descuenta'),
    ('no','NO se descuenta'),
]


class ResPartner(models.Model): 
    _inherit = 'res.partner'

    price_type = fields.Selection([('fijo', 'Precio Fijo'), ('variable', 'Precio Variable')], string='Tipo de precio')
    commission_percentage = fields.Selection(porcentajes, string="% de Comision")
    freight_in = fields.Selection(Flete_opciones, string="Flete de entrada?")
    mx_customs = fields.Selection(Flete_opciones, string="Aduana MX?")
    us_customs = fields.Selection(Flete_opciones, string="Aduana US?")
    in_and_out = fields.Selection(InOut_opciones, string="In and Out?")
    box = fields.Selection(InOut_opciones, string="Caja?")
    
    reference = fields.Char(string="Referencia")

    Desc_fijo = fields.Char('Descuentos Fijos')