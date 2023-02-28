from odoo import models, fields, api, _


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    disable = fields.Boolean('deshabilitar ?')
