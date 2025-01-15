from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools



class InventoryatdateReport(models.Model):
    _name = "inventoryatdate.report"
    _description = "Inventory at date Report"
    _auto = False


    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot', readonly=True)
    quantity = fields.Float('Quantity', readonly=True, group_operator="sum")
    price = fields.Float('Unit price', readonly=True, group_operator="avg")
    total = fields.Float('Total', readonly=True, group_operator="sum")
    # price_average = fields.Float('Average Cost', readonly=True, group_operator="avg")
    # nbr_lines = fields.Integer('# of Lines', readonly=True)
    # category_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    # product_tmpl_id = fields.Many2one('product.template', 'Product Template', readonly=True)
    # country_id = fields.Many2one('res.country', 'Partner Country', readonly=True)
    # fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', readonly=True)
    # account_analytic_id = fields.Many2one('account.analytic.account', 'Anaytic Account', readonly=True)


    @api.model
    def generate_report(self, fecha):
        mytime = time(6,0,0)
        fecha_final = datetime.combine(fecha, mytime)
        mytime = time(18,0,0)
        fecha_inicial = datetime.combine(fecha, mytime) - relativedelta(months=3)
        fecha_final = fecha_final + relativedelta(hours=18)
        print(fecha_inicial)
        print(fecha_final)
        tools.drop_view_if_exists(self.env.cr, "inventoryatdate_report")
        #fecha_inicial = fecha.replace(hour=18, minute=0, second=0) - relativedelta(months=3)
        query = """CREATE OR REPLACE VIEW inventoryatdate_report AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY product_id) AS id,
        id AS lot_id, 
        product_id, 
        suma AS quantity, 
        precio_comparado AS price, 
        ROUND((COALESCE(suma, 0) * COALESCE(precio_comparado, 0))::numeric, 2) AS total
    FROM (
        SELECT 
            lote.id, 
            lote.product_id, 
            sale.qty_ventas, 
            scrap.qty_scrap, 
            repack.qty_repack, 
            stock.qty_stock,
            COALESCE(sale.qty_ventas, 0) + COALESCE(scrap.qty_scrap, 0) + 
            COALESCE(repack.qty_repack, 0) + COALESCE(stock.qty_stock, 0) AS suma,
            GREATEST(dat.price_unit, datp.price_unit) AS precio_comparado
        FROM (
            SELECT id, product_id, parent_lod_id 
            FROM public.stock_production_lot 
            WHERE create_date BETWEEN '{0}' AND '{1}'
        ) AS lote
        LEFT JOIN (
            SELECT 
                lot_id, 
                SUM(qty_done) AS qty_ventas
            FROM public.stock_move_line
            WHERE date > '{1}' 
              AND lot_id IN (
                  SELECT id 
                  FROM public.stock_production_lot 
                  WHERE create_date BETWEEN '{0}' AND '{1}'
              ) 
              AND location_dest_id = 5
            GROUP BY lot_id
        ) AS sale ON lote.id = sale.lot_id
        LEFT JOIN (
            SELECT 
                lot_id, 
                SUM(scrap_qty) AS qty_scrap
            FROM public.stock_scrap
            WHERE date_done > '{1}' 
              AND lot_id IN (
                  SELECT id 
                  FROM public.stock_production_lot 
                  WHERE create_date BETWEEN '{0}' AND '{1}'
              )
            GROUP BY lot_id
        ) AS scrap ON lote.id = scrap.lot_id
        LEFT JOIN (
            SELECT 
                lot_id, 
                SUM(qty_done) AS qty_repack
            FROM public.stock_move_line
            WHERE lot_id IN (
                  SELECT id 
                  FROM public.stock_production_lot 
                  WHERE create_date BETWEEN '{0}' AND '{1}'
              )
              AND date > '{1}' 
              AND location_dest_id = 14
            GROUP BY lot_id
        ) AS repack ON lote.id = repack.lot_id
        LEFT JOIN (
            SELECT 
                lot_id, 
                quantity AS qty_stock
            FROM stock_quant
            WHERE location_id = 8 
              AND lot_id IN (
                  SELECT id 
                  FROM public.stock_production_lot 
                  WHERE create_date BETWEEN '{0}' AND '{1}'
              )
        ) AS stock ON lote.id = stock.lot_id
        LEFT JOIN (
            SELECT 
                spl.id, 
                spl.name, 
                pol.price_unit AS price_unit
            FROM stock_production_lot AS spl
            JOIN (
                SELECT DISTINCT ON (lot_id) 
                    sml.id, 
                    sm.purchase_line_id, 
                    sml.lot_id
                FROM stock_move_line sml
                JOIN stock_move sm ON sml.move_id = sm.id
                WHERE sm.location_id = 4 
                  AND sm.location_dest_id = 9
            ) AS sm ON spl.id = sm.lot_id
            JOIN purchase_order_line pol ON sm.purchase_line_id = pol.id
            WHERE spl.create_date BETWEEN '{0}' AND '{1}'
        ) AS dat ON lote.id = dat.id
        LEFT JOIN (
            SELECT 
                spl1.id, 
                spl1.name, 
                pol1.price_unit AS price_unit
            FROM stock_production_lot AS spl1
            JOIN (
                SELECT DISTINCT ON (lot_id) 
                    sml.id, 
                    sm.purchase_line_id, 
                    sml.lot_id
                FROM stock_move_line sml
                JOIN stock_move sm ON sml.move_id = sm.id
                WHERE sm.location_id = 4 
                  AND sm.location_dest_id = 9
            ) AS sm1 ON spl1.id = sm1.lot_id
            JOIN purchase_order_line pol1 ON sm1.purchase_line_id = pol1.id
            WHERE spl1.create_date BETWEEN '{0}' AND '{1}'
        ) AS datp ON lote.parent_lod_id = datp.id
    ) AS sub
    WHERE sub.suma > 0 
      AND product_id <> 561
)
        """.format(fecha_inicial.strftime("%Y-%m-%d %H:%M:%S"), fecha_final.strftime("%Y-%m-%d %H:%M:%S"))

        self.env.cr.execute(query)

    # def init(self):
    #     # self._table = sale_report
    #     tools.drop_view_if_exists(self.env.cr, self._table)
    #     self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
    #         %s
    #         FROM ( %s )
    #         %s
    #         )""" % (self._table, self._select(), self._from(), self._group_by()))

    # def _select(self):
    #     select_str = """
    #         WITH currency_rate as (%s)
    #             SELECT
    #                 po.id as order_id,
    #                 min(l.id) as id,
    #                 po.date_order as date_order,
    #                 po.state,
    #                 po.date_approve,
    #                 po.dest_address_id,
    #                 po.partner_id as partner_id,
    #                 po.user_id as user_id,
    #                 po.company_id as company_id,
    #                 po.fiscal_position_id as fiscal_position_id,
    #                 l.product_id,
    #                 p.product_tmpl_id,
    #                 t.categ_id as category_id,
    #                 po.currency_id,
    #                 t.uom_id as product_uom,
    #                 extract(epoch from age(po.date_approve,po.date_order))/(24*60*60)::decimal(16,2) as delay,
    #                 extract(epoch from age(l.date_planned,po.date_order))/(24*60*60)::decimal(16,2) as delay_pass,
    #                 count(*) as nbr_lines,
    #                 sum(l.price_total / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as price_total,
    #                 (sum(l.product_qty * l.price_unit / COALESCE(po.currency_rate, 1.0))/NULLIF(sum(l.product_qty/line_uom.factor*product_uom.factor),0.0))::decimal(16,2) as price_average,
    #                 partner.country_id as country_id,
    #                 partner.commercial_partner_id as commercial_partner_id,
    #                 analytic_account.id as account_analytic_id,
    #                 sum(p.weight * l.product_qty/line_uom.factor*product_uom.factor) as weight,
    #                 sum(p.volume * l.product_qty/line_uom.factor*product_uom.factor) as volume,
    #                 sum(l.price_subtotal / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as untaxed_total,
    #                 sum(l.product_qty / line_uom.factor * product_uom.factor) as qty_ordered,
    #                 sum(l.qty_received / line_uom.factor * product_uom.factor) as qty_received,
    #                 sum(l.qty_invoiced / line_uom.factor * product_uom.factor) as qty_billed,
    #                 case when t.purchase_method = 'purchase' 
    #                      then sum(l.product_qty / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
    #                      else sum(l.qty_received / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
    #                 end as qty_to_be_billed
    #     """ % self.env['res.currency']._select_companies_rates()
    #     return select_str

    # def _from(self):
    #     from_str = """
    #         purchase_order_line l
    #             join purchase_order po on (l.order_id=po.id)
    #             join res_partner partner on po.partner_id = partner.id
    #                 left join product_product p on (l.product_id=p.id)
    #                     left join product_template t on (p.product_tmpl_id=t.id)
    #             left join uom_uom line_uom on (line_uom.id=l.product_uom)
    #             left join uom_uom product_uom on (product_uom.id=t.uom_id)
    #             left join account_analytic_account analytic_account on (l.account_analytic_id = analytic_account.id)
    #             left join currency_rate cr on (cr.currency_id = po.currency_id and
    #                 cr.company_id = po.company_id and
    #                 cr.date_start <= coalesce(po.date_order, now()) and
    #                 (cr.date_end is null or cr.date_end > coalesce(po.date_order, now())))
    #     """
    #     return from_str

    # def _group_by(self):
    #     group_by_str = """
    #         GROUP BY
    #             po.company_id,
    #             po.user_id,
    #             po.partner_id,
    #             line_uom.factor,
    #             po.currency_id,
    #             l.price_unit,
    #             po.date_approve,
    #             l.date_planned,
    #             l.product_uom,
    #             po.dest_address_id,
    #             po.fiscal_position_id,
    #             l.product_id,
    #             p.product_tmpl_id,
    #             t.categ_id,
    #             po.date_order,
    #             po.state,
    #             line_uom.uom_type,
    #             line_uom.category_id,
    #             t.uom_id,
    #             t.purchase_method,
    #             line_uom.id,
    #             product_uom.factor,
    #             partner.country_id,
    #             partner.commercial_partner_id,
    #             analytic_account.id,
    #             po.id
    #     """
    #     return group_by_str