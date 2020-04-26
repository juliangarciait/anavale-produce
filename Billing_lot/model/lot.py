from odoo import api, fields, models

class LotDatos(models.Model):
     _inherit = 'stock.production.lot'
     
     @api.model
     def create(self, vals_list):
        res = super(LotDatos, self).create(vals_list)
        for lot in res:
            if not lot['ref']:
                lot['ref'] = 'ORG'
            vals = {
                'name':lot.name
            }
            self.env['account.analytic.tag'].create(vals)
        return res

#     ExtBills = fields.One2many('account.move', 'LotId', help='bill en este lote')

