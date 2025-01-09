from odoo import models, fields, api

class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    def action_reset_next_number(self):
        """
        Método para restablecer el campo `number_next` a 1 para las secuencias seleccionadas.
        """
        for record in self:
            record.number_next = 1 