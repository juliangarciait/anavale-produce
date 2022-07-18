# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import time 
from odoo.exceptions import ValidationError
import logging
import re

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    lot_reference = fields.Text('Lot Reference', compute='_compute_lot_reference')


    @api.depends('partner_id', 'purchase_id')
    def _compute_lot_reference(self):
        for invoice in self: 
            invoice.lot_reference = ''
            purchase = self.env['purchase.order'].search([('invoice_ids', 'in', [invoice.id])])
            if purchase:    
                picking = self.env['stock.picking'].search([('purchase_id', '=', purchase.id), ('state', '=', 'done')], order='create_date desc', limit=1)
                move = self.env['stock.move'].search([('picking_id', '=', picking.id)], limit=1)
                reference = move.lot_id.name
                if reference: 
                    reference = re.sub(str(move.product_id.product_tmpl_id.lot_code_prefix), '', reference)
                    reference = re.sub(str(move.product_id.product_template_attribute_value_ids[0].product_attribute_value_id.name), '', reference)

                    invoice.lot_reference = reference
                

    @api.onchange('invoice_line_ids')
    def onchange_invoice_line_ids(self):
        list_mapped = []
        for line in self.invoice_line_ids:
            if (line.product_id, line.lot_id) in list_mapped:
                raise ValidationError('Product {} with Lot {}! Already exist on the Invoice Lines. Please add amount in '
                                'existing line'.format(
                    str(line.product_id.name), line.lot_id.name))
            list_mapped.append((line.product_id, line.lot_id))