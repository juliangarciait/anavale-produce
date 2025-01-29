
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
    def _get_columns_name(self, options):
        columns = super(ReportAccountAgedPartner, self)._get_columns_name(options)
        if self._description == 'Aged Receivable':
            columns[1].update({'name':'Comments//Due date'})
            columns[2].update({'name':'Last payment'})
            columns[3].update({'name':''})
            columns[4].update({'name':'Pay Terms'})
        return columns
    

    def action_partner_reconcile(self, options, params, *args, **kwargs):
        partner_id = params.get('partner_id')
        if not partner_id:
            return {}

        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Partner',
        #     'res_model': 'res.partner',
        #     'view_mode': 'form',
        #     'view_type': 'form',
        #     'res_id': partner_id,
        #     'target': 'current',  # 'new' para abrir en un pop-up
        #     'context': self.env.context,
        # }
        form = self.env.ref('base.view_partner_form', False)
        return {'name': 'test',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': partner_id,
                'target': 'current',
                'views': [[form.id, 'form']],
                'flags': {'form': {'action_buttons': True}}
                }
    
        # form = self.env.ref('base.view_partner_form', False)
        # ctx = self.env.context.copy()
        # ctx['partner_ids'] = ctx['active_id'] = [params.get('partner_id')]
        # return {
        #     'type': 'ir.actions.client',
        #     'view_id': form.id,
        #     #'tag': form.tag,
        #     'context': ctx,
        # }




    @api.model
    def _get_lines(self, options, line_id=None):
        # Llamar al método original para obtener las líneas
        lines = super(ReportAccountAgedPartner, self)._get_lines(options, line_id)

        # Agregar el campo `comment` del partner
        if self._description == 'Aged Receivable':
            for line in lines:
                if line.get('partner_id'):
                    partner = self.env['res.partner'].browse(line['partner_id'])
                    comment = partner.comment or ''
                    line.update({"comment":comment})
                    payment = self.env['account.payment'].search([('partner_id', '=', partner.id)], order='payment_date desc', limit=1)
                    line.update({"ultimo_pago":str(payment.payment_date)})
                    if 'columns' in line:
                        line['columns'][0] = {'name':comment}
                        line['columns'][1] = {'name':str(payment.payment_date or '')}
                        

                    #line['comment'] += f" ({comment})" if comment else "
                elif line.get('caret_options')=='account.invoice.out':
                    line['columns'][1] = {'name':''}
                    term = self.env['account.move'].search([('name','=',line['name'])], limit=1)
                    line['columns'][2] = {'name':str(term.payment_comments or '')}
                    
                    line['columns'][3] = {'name':term.invoice_payment_term_id.name}


        return lines
    

class InvoiceAccountAgedPartner(models.AbstractModel):
    _inherit = 'account.move'

    payment_comments = fields.Char("Comentario de Pago")

