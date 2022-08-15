
from odoo import models, api, fields, _
from odoo.tools.misc import format_date

class report_account_aged_partner_saleman(models.AbstractModel):
    _name = "account.aged.partner.saleman"
    _description = "Aged Partner Balances"
    _inherit = 'account.aged.partner'

    filter_salesman = True

    @api.model
    def _init_filter_salesman(self, options, previous_options=None):
        if not self.filter_salesman:
            return

        options['salesman'] = True
        options['salesman_ids'] = previous_options and previous_options.get('salesman_ids') or []
        selected_salesman_ids = [int(salesman) for salesman in options['salesman_ids']]
        selected_salesman = selected_salesman_ids and self.env['res.users'].browse(selected_salesman_ids) or self.env[
            'selected_salesman_ids']
        options['selected_salesman_ids'] = selected_salesman.mapped('name')

    @api.model
    def _get_options_salesman_domain(self, options):
        domain = []
        if options.get('salesman_ids'):
            salesman_ids = [int(salesman) for salesman in options['salesman_ids']]
            domain.append(('salesman_id', 'in', salesman_ids))
        return domain
