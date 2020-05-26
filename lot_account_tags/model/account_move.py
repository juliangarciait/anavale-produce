from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_sel_account(self):
        if self.product_id:
            #domain = [('name', '=', self.lot_id.account_tag_id)]
            #res = self.env['account.analytic.tag'].search(domain)
            self.analytic_account_id = self.product_id.product_tmpl_id.analytic_account_id