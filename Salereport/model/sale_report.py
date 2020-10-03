# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)



class SaleReport(models.Model):
    _inherit = "sale.report"

    def _test_calculate(self):
        _logger.info("")


    lot_id = fields.Char('Lots', readonly=True)
    avg_price = fields.Float('Average Price', readonly=True, group_operator="avg")
    test_calculate = fields.Float('Test Calculate', compute=_test_calculate)
    # average = fields.Float('Average Price1', store=True, compute='_compute_avg_price')

    # @api.depends('product_uom_qty', 'price_total')
    # def _compute_avg_price(self):
    #     for line in self:
    #         res=line

    """
    fields['avg_price'] = ", ((sum(l.price_total / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE " \
                              "s.currency_rate END))/CASE (sum(l.qty_invoiced / u.factor * u2.factor)) WHEN 0 THEN " \
                              "1.0 ELSE  (sum(l.qty_invoiced / u.factor * u2.factor)) END)  as avg_price "
    """


    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['lot_id'] = ", lot.name as lot_id"
        #fields['avg_price'] = ",   (ROUND(sum(price_subtotal),2) / (ROUND((CASE (sum(product_uom_qty)) WHEN 0 THEN " \
        #                      "1.0 ELSE (sum(product_uom_qty)) END  ),2))) as avg_price "

        #fields['avg_price'] = ", ((sum(l.price_total / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE " \
        #                      "s.currency_rate END))/CASE (sum(l.qty_invoiced / u.factor * u2.factor)) WHEN 0 THEN " \
        #                      "1.0 ELSE  (sum(l.qty_invoiced / u.factor * u2.factor)) END)  as avg_price "

        fields['avg_price'] = ",   CASE WHEN (COUNT(s.id)) >0 THEN (SUM(CASE product_uom_qty WHEN 0 THEN 0.0 ELSE " \
                              "price_subtotal/product_uom_qty END)/count(s.id))    ELSE (MAX(CASE product_uom_qty " \
                              "WHEN 0 THEN 0.0 ELSE price_subtotal/product_uom_qty END)/count(s.id)) END avg_price "

        groupby += ', lot.name'
        from_clause = ' left join stock_production_lot lot on (l.lot_id=lot.id)'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
