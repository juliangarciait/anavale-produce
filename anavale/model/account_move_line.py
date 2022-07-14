# -*- coding: utf-8 -*-

from ofxparse import Account
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    lot_id = fields.Many2one('stock.production.lot', string='Lot')

    tags_text = fields.Text(string='Analytic Tags', compute='_compute_analytic_tags', store=False)


    @api.onchange('lot_id')
    def onchange_lot_id(self):
        if self.lot_id:
            self.name = self.lot_id.name
            self.analytic_tag_ids = self.lot_id.analytic_tag_ids


    @api.depends('analytic_tag_ids')
    def _compute_analytic_tags(self): 
        for record in self:
            names = []
            for tags in record.analytic_tag_ids:
                names.append(tags.name)
            
            record.tags_text = ', '.join(filter(bool, names))


    def write(self, vals): 
        res = super(AccountMoveLine, self).write(vals)

        for line in self: 
            sale = self.env['sale.order.line'].search([('invoice_lines', 'in', [line.id])])
            if line.purchase_line_id: 
                line.purchase_line_id.price_unit = line.price_unit
            elif sale:
                sale.price_unit = line.price_unit
            else: 
                continue

        return res
        
