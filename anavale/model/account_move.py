# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('invoice_line_ids')
    def onchange_invoice_line_ids(self):
        list_mapped = []
        for line in self.invoice_line_ids:
            if (line.product_id, line.lot_id) in list_mapped:
                raise ValidationError('Product {} with Lot {}! Already exist on the Invoice Lines. Please add amount in '
                                'existing line'.format(
                    str(line.product_id.name), line.lot_id.name))
            list_mapped.append((line.product_id, line.lot_id))