# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class FilteredAgedReceivable(models.TransientModel): 
    _name = 'filtered.aged.receivable'

    user_ids = fields.Many2many('res.users')

    def confirm(self): 
        partner_ids = self.env['res.partner'].search([('user_id', 'in', self.user_ids.ids)])
        return {
            'type'           : "ir.actions.client", 
            'name'           : _("Aged Receivable"),
            'tag'            : "account_report", 
            'options'        : {"partner_ids" : partner_ids.ids},
            'ignore_session' : "both", 
            'context'        : "{'model' : 'account.aged.receivable'}" 
        }
    
    def confirm_auto(self): 
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        partner_ids = self.env['res.partner'].search([('user_id', 'in', user.ids)])
        return {
            'type'           : "ir.actions.client", 
            'name'           : _("Aged Receivable"),
            'tag'            : "account_report", 
            'options'        : {"partner_ids" : partner_ids.ids},
            'ignore_session' : "both", 
            'context'        : "{'model' : 'account.aged.receivable'}" 
        }