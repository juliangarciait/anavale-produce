from odoo import api, fields, models, tools

class BudgetReport(models.Model):
    _name = 'report.sales.salesman'
    _description = 'Reporte Ventas por vendedor'
    _auto = False  # importante: porque es una vista, no tabla

    salesman_id = fields.Many2one('res.user', string='Vendedor')
    quantity_sold_today = fields.Float(string='Venta hoy')
    quantity_sold_month = fields.Float(string='Venta mes')
    quantity_sold_last_year = fields.Float(string='Venta año')


    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE OR REPLACE VIEW %s
 AS
 WITH sales_today AS (
         SELECT so.user_id AS salesman_id,
            sum(sol.product_uom_qty) AS quantity_sold_today
           FROM sale_order_line sol
             JOIN sale_order so ON sol.order_id = so.id
          WHERE (so.state::text = ANY (ARRAY['sale'::character varying::text, 'done'::character varying::text])) AND so.date_order::date = CURRENT_DATE
          GROUP BY so.user_id
        ), sales_month AS (
         SELECT so.user_id AS salesman_id,
            sum(sol.product_uom_qty) AS quantity_sold_month
           FROM sale_order_line sol
             JOIN sale_order so ON sol.order_id = so.id
          WHERE (so.state::text = ANY (ARRAY['sale'::character varying::text, 'done'::character varying::text])) AND date_part('year'::text, so.date_order) = date_part('year'::text, CURRENT_DATE) AND date_part('month'::text, so.date_order) = date_part('month'::text, CURRENT_DATE)
          GROUP BY so.user_id
        ), sales_last_year AS (
         SELECT so.user_id AS salesman_id,
            sum(sol.product_uom_qty) AS quantity_sold_last_year
           FROM sale_order_line sol
             JOIN sale_order so ON sol.order_id = so.id
          WHERE (so.state::text = ANY (ARRAY['sale'::character varying::text, 'done'::character varying::text])) AND date_part('year'::text, so.date_order) = (date_part('year'::text, CURRENT_DATE) - 1::double precision) AND date_part('month'::text, so.date_order) = date_part('month'::text, CURRENT_DATE)
          GROUP BY so.user_id
        )
 SELECT row_number() OVER () AS id,  
    u.id AS salesman_id,
    COALESCE(st.quantity_sold_today, 0::numeric) AS quantity_sold_today,
    COALESCE(sm.quantity_sold_month, 0::numeric) AS quantity_sold_month,
    COALESCE(sly.quantity_sold_last_year, 0::numeric) AS quantity_sold_last_year
   FROM res_users u
     LEFT JOIN res_partner rp ON u.partner_id = rp.id
     LEFT JOIN sales_today st ON u.id = st.salesman_id
     LEFT JOIN sales_month sm ON u.id = sm.salesman_id
     LEFT JOIN sales_last_year sly ON u.id = sly.salesman_id
  WHERE COALESCE(st.quantity_sold_today, 0::numeric) > 0::numeric OR COALESCE(sm.quantity_sold_month, 0::numeric) > 0::numeric
  ORDER BY (COALESCE(st.quantity_sold_today, 0::numeric)) DESC, (COALESCE(sm.quantity_sold_month, 0::numeric)) DESC""" % (self._table))


