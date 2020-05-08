from odoo import api, fields, models

class LotDatos(models.Model):
     _inherit = 'stock.production.lot'
     
     @api.model
     def create(self, vals_list):
        res = super(LotDatos, self).create(vals_list)
        for lot in res:
            if not lot['ref']:
                lot['ref'] = 'ORG'
            tag_lot = lot.name[2:12]
            vals = {
                'name': tag_lot
            }
            account_tag = self.env['account.analytic.tag'].search([('name', '=', tag_lot),])
            if not account_tag:
                self.env['account.analytic.tag'].create(vals)
        return res

#     ExtBills = fields.One2many('account.move', 'LotId', help='bill en este lote')

