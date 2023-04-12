# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

Precios = [
    ('fijo', 'Precio Fijo'),
    ('variable', 'Precio Variable'),
]

porcentajes = [
    ('8', '8% comision'),
    ('9', '9% comision'),
    ('10', '10% comision'),
    ('11', '11% comision'),
    ('12', '12% comision'),

]

SiNo = [
    ('si','SI'),
    ('no','NO'),
]

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    tipo_precio = fields.Selection(Precios, string="Tipo de Precio")
    
    porcentaje_comision = fields.Selection(porcentajes, string="% de Comision")

    Flete_entrada = fields.Selection(SiNo, string='Flete de entrada?')

    Aduana_MX = fields.Selection(SiNo, string='Aduana MX?')

    Aduana_US = fields.Selection(SiNo, string='Aduana US?')

    In_out = fields.Selection(SiNo, string='In and Out?')

    caja = fields.Selection(SiNo, string='caja?')

    referencia = fields.Text('Referencia')
    
    lot_code_prefix = fields.Char('Lot Code', help='Code used to compute automatic Lot Numbers, 3 letters.', size=3)
    sequence_id = fields.Many2one('ir.sequence', string='Lot Sequence',
        help="This field contains the information related to the numbering of the Lots purchased to this Vendor", copy=False)
    
    _sql_constraints = [
        ('lot_code_prefix_uniq', 'unique (lot_code_prefix)', "This Lot Code Prefix is already used in another Vendor!.")
    ]
    
    def action_create_vendor_sequence(self):
        self.ensure_one()
        if not self.lot_code_prefix:
            raise ValidationError('Enter "Lot Code" and try again!')
        data = {'name': 'Vendor Lot Sequence - %s' % self.lot_code_prefix,
                'code': 'production.lot.%s.sequence' % self.lot_code_prefix.lower(),
                'prefix': '%(y)s-',
                'padding': 4 }
        seq = self.env['ir.sequence'].create(data)
        self.sequence_id = seq.id
        
    def action_change_vendor_sequence(self):
        wiz = self.env['partner.sequence.change.wizard'].create({'partner_id': self.id, 'sequence_id': self.sequence_id.id})
        return {'type': 'ir.actions.act_window',
                'res_model': 'partner.sequence.change.wizard',
                'view_mode': 'form',
                'res_id': wiz.id,
                'target': 'new'}