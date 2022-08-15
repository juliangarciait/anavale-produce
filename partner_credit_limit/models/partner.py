# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    over_credit = fields.Boolean('Allow Over Credit?')
    credit_insured = fields.Float(string='Asegurado')
    credit_manual = fields.Float(string='Manual')

    @api.onchange('credit_insured', 'credit_manual')
    def onchange_credito(self):
        self.credit_limit = self.credit_insured
        if self.credit_manual > self.credit_insured:
            self.credit_limit = self.credit_manual


