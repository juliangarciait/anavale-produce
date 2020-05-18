from odoo import api, fields, models


class LotData(models.Model):
    _inherit = 'stock.production.lot'

    account_tag_id = fields.Many2one('account.analytic.tag', string='Accounting Tag',
                                     help="This field contains the information related to the account tag for this lot",
                                     copy=False)

    @api.model
    def create(self, vals_list):
        res = super(LotData, self).create(vals_list)
        for lot in res:
            if not lot['ref']:
                lot['ref'] = 'ORG'
            # busqueda de elementos del account tag
            lot_name = lot.name
            vendor_prefix_idx = [x.isdigit() for x in lot_name].index(True)  # inicio del vendor
            vendor_prefix_len = [x.isdigit() for x in lot_name[vendor_prefix_idx:]].index(
                True)  # encuentra los caracteres del vendor pueden ser 2 o 3
            tag_lot = lot_name[vendor_prefix_idx: (
                        vendor_prefix_idx + vendor_prefix_len + 7)]  # se saca determina nombre para tag venxx-xxxx
            account_tag = self.env['account.analytic.tag'].search([('name', '=', tag_lot)])  # busca account_tag
            if not account_tag:
                vals = {
                    'name': tag_lot
                        }
                account_tag = self.env['account.analytic.tag'].create([vals)  # si no existe la crea
            lot.account_tag_id = account_tag
        return res