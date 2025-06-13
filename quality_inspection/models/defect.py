from odoo import models, fields

class Defect(models.Model):
    _name = 'defect'
    _description = 'Defect'

    name = fields.Char(string='Defect Name', required=True)
