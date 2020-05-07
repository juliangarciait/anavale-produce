# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class PartnerChangeSequenceWizard(models.TransientModel):
    _name = 'partner.sequence.change.wizard'
    _description = 'Change Vendor Sequence'
    
    partner_id = fields.Many2one('res.partner', required=True, readonly=True)
    sequence_id = fields.Many2one('ir.sequence', string='Lot Sequence', required=True, readonly=True)    
    number_next = fields.Integer(string='Next Number', readonly=True, related="sequence_id.number_next")
    last_used_number = fields.Integer(string='Last Lot number in Stock', compute='_compute_last_used_number')
    new_number_next = fields.Integer(string='New Next Number')
    
    @api.constrains('new_number_next')
    def _constraint_new_number_next(self):
        for record in self:
            if record.new_number_next <= record.last_used_number:
                raise UserError("Next sequence number must be greater than %s" % record.last_used_number)
            
    def _compute_last_used_number(self):
        for record in self:
            last_seq = self.env['stock.production.lot'].search([('name', 'ilike', record.partner_id.lot_code_prefix)], order='id DESC', limit=1)
            if last_seq:
                start = last_seq.name.find(record.partner_id.lot_code_prefix) + len(record.partner_id.lot_code_prefix) + 3
                end = start + 4
                record.last_used_number = int(last_seq.name[start:end])
                record.new_number_next = record.last_used_number + 1
            else:
                record.last_used_number = False
                
    def update_number_next(self):
        for record in self:
            record.sequence_id.number_next = record.new_number_next