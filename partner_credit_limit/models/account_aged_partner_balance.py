from odoo import models, api, fields, _
from odoo.tools.misc import format_date

class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = 'account.aged.partner'

    @api.model
    def _get_columns_name(self, options):
        columns = super(ReportAccountAgedPartner, self)._get_columns_name(options)
        if self._description == 'Aged Receivable':
            columns[3].update({'name':'Asegurado'})
            
        return columns
    
    @api.model
    def _get_lines(self, options, line_id=None):
        # Llamar al método original para obtener las líneas
        lines = super(ReportAccountAgedPartner, self)._get_lines(options, line_id)

        # Agregar el campo `comment` del partner
        if self._description == 'Aged Receivable':
            for line in lines:
                if line.get('partner_id'):
                    partner = self.env['res.partner'].browse(line['partner_id'])
                    credito_asegurado = partner.credit_insured or 0
                    line.update({"Asegurado":credito_asegurado})
                    if 'columns' in line:
                        line['columns'][2] = {'name':'${:,.2f}'.format(credito_asegurado)}
                        


        return lines