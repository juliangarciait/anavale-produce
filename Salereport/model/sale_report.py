# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    lot_id = fields.Char('Lots', readonly=True)
    avg_price = fields.Float('Average Price', readonly=True, group_operator="avg")
    invoice_date_due = fields.Date(related='order_id.invoice_ids.invoice_date', string="Invoice Date", readonly=True, stored=True)
    # average = fields.Float('Average Price1', store=True, compute='_compute_avg_price')

    # @api.depends('product_uom_qty', 'price_total')
    # def _compute_avg_price(self):
    #     for line in self:
    #         res=line


    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['lot_id'] = ", lot.name as lot_id"
        fields['avg_price'] = ", (sum(price_subtotal)/ case sum(product_uom_qty) when 0 then 1.0 else sum(product_uom_qty) end) as avg_price"
        groupby += ', lot.name'
        from_clause = ' left join stock_production_lot lot on (l.lot_id=lot.id)'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
