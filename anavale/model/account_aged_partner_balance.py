
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


class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = 'account.aged.partner'

    @api.model
    def _get_lines(self, options, line_id=None):
        # Llamar al método original para obtener las líneas
        lines = super(ReportAccountAgedPartner, self)._get_lines(options, line_id)

        # Agregar el campo `comment` del partner
        for line in lines:
            if line.get('partner_id'):
                partner = self.env['res.partner'].browse(line['partner_id'])
                comment = partner.comment or ''
                line.update({"comment":comment})
                payment = self.env['account.payment'].search([('partner_id', '=', partner.id)], order='payment_date desc', limit=1)
                line.update({"ultimo_pago":str(payment.payment_date)})
                #line['comment'] += f" ({comment})" if comment else ""

        return lines