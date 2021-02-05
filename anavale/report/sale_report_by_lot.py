# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.addons.helpdesk.models.helpdesk_ticket import TICKET_PRIORITY


class SaleReportAvg(models.Model):
    _name = 'sale.report.by.lot'
    _description = "Sale Report By Lot"
    _auto = False
    _order = 'id DESC'

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    #create_date = fields.Date("Sale Create Date", readonly=True)
    lot_id = fields.Many2one('stock.production.lot', string='Lot', readonly=True)
    qty_sale = fields.Float(string='Qty Sale', readonly=True)
    total_amount = fields.Float(string='Total Amount', readonly=True)
    qty_invoiced = fields.Float(string='Qty Invoiced', readonly=True)
    avg_price = fields.Float(string='Avg Price', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    description = fields.Char(
        string='Description',
        compute='_compute_description')


    @api.depends('product_id', 'lot_id')
    def _compute_description(self):
        for rec in self:
            if rec.product_id and rec.lot_id:
                rec.description = "%s (%s)" % (rec.lot_id.name, rec.product_id.name_get()[0][1])

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'sale_report_by_lot')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW sale_report_by_lot AS (
                SELECT	row_number() OVER () as id,s.company_id as company_id,l.product_id as product_id,
                        sum(l.product_uom_qty / u.factor * u2.factor) as qty_sale,
                        lot.id as lot_id,
                        (ROUND(sum(l.price_total / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END),2))+
                        COALESCE(MAX(grouped_lot_id.price_total_childs),0) as total_amount,
                        
                        ((ROUND(sum(l.qty_invoiced / u.factor * u2.factor),2)) +
                         (COALESCE(MAX(grouped_lot_id.qty_invoiced_childs),0))) as qty_invoiced,
                        
                        
                        ROUND((CASE round(sum(l.product_uom_qty / u.factor * u2.factor),2) 
                            WHEN 0.0 THEN 0.0 
                            ELSE (ROUND(sum(l.price_total / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END),2))/
                            (round(sum(l.product_uom_qty / u.factor * u2.factor),2)) END ),2) as avg_price
                            
                    FROM 
                    sale_order_line l
                          join sale_order s on (l.order_id=s.id)
                          join res_partner partner on s.partner_id = partner.id
                            left join product_product p on (l.product_id=p.id)
                                left join product_template t on (p.product_tmpl_id=t.id)
                        left join uom_uom u on (u.id=l.product_uom)
                        left join uom_uom u2 on (u2.id=t.uom_id)
                        left join product_pricelist pp on (s.pricelist_id = pp.id)
                     left join stock_production_lot lot on (l.lot_id=lot.id)
                     LEFT JOIN
                        (	SELECT 
                                lot.parent_lod_id , 
                                ROUND(sum(l.price_total / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END),2) as price_total_childs,
                                ROUND(sum(l.qty_invoiced / u.factor * u2.factor),2) as qty_invoiced_childs
                            FROM 
                                sale_order_line l
                                      join sale_order s on (l.order_id=s.id)
                                      join res_partner partner on s.partner_id = partner.id
                                        left join product_product p on (l.product_id=p.id)
                                            left join product_template t on (p.product_tmpl_id=t.id)
                                    left join uom_uom u on (u.id=l.product_uom)
                                    left join uom_uom u2 on (u2.id=t.uom_id)
                                    left join product_pricelist pp on (s.pricelist_id = pp.id)
                                 left join stock_production_lot lot on (l.lot_id=lot.id)
                                WHERE l.product_id IS NOT NULL--
                                    AND s.state NOT IN ('cancel','draft')
                                    AND lot.name IS NOT NULL
                                    AND lot.parent_lod_id IS NOT NULL
                                     GROUP BY 
                                    lot.parent_lod_id 
                        ) grouped_lot_id
                            ON lot.id = grouped_lot_id.parent_lod_id                           
                    
                     WHERE l.product_id IS NOT NULL--
                        AND s.state NOT IN ('cancel','draft')
                        AND lot.name IS NOT NULL 
                        AND lot.parent_lod_id IS NULL
                        AND l.create_date >= %s
						AND l.create_date <= %s
                    --and lot.name = '09UPC20-0051'
                     GROUP BY 
                        s.company_id,                        
                        l.product_id,
                        lot.id
                )
            """, (self.env.context.get('date_from'), self.env.context.get('date_to')))
