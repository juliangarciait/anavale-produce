from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('lot_id')
    def _onchange_lot_sel_account(self):
        if self.lot_id:
            domain = [('name', '=', self.lot_id.name[2:12])]
            res = self.env['account.analytic.tag'].search(domain)
            self.analytic_tag_ids = res




    # @api.model
    # def create(self, vals_list):
    #     res = super(SaleOrderLine, self).create(vals_list)
    #     for line in res:
    #         domain = [('name', '=', line.lot_id.name)]
    #         line.analytic_line_ids = self.env['account.analytic.account'].search(domain)
    #     return res

    #         res = self._get_account_analitycs(self.lot_id.id)
    #         quantity = res['quantity']
    #         self.product_uom_qty = 0.0
    #         # wt = self.env['account.analytic.account']
    #         # self.analytic_line_ids = wt.search([('name', '=', self.lot_id.name)]).id

    # def _get_account_analitycs(self):

    #     account_ids = []        
    #     avail = {}
    #     domain = [('name', '=', self.lot_id.name)]
    #     for so in self.env['account.analytic.account'].search(domain):
    #         avail.setdefault(so.lot_id.id, {'lot': so.lot_id.id, 'qty': 0.0}) #me quede en probar esto en python haber que suelta
    #         avail[so.lot_id.id]['qty'] -= so.qty_to_deliver 
         
    #     for lot in avail:
    #         if float_compare( avail[lot]['qty'], 0, precision_rounding=rounding) > 0:
    #            lot_ids.append(lot) 
    #            quantity += avail[lot]['qty']
        
    #     return {'lot_ids': lot_ids, 'quantity': quantity}