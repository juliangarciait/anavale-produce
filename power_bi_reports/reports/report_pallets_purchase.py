from odoo import api, fields, models, tools

class BudgetReport(models.Model):
    _name = 'report.pallets.purchase'
    _description = 'Reporte Pallets Compras'
    _auto = False  # importante: porque es una vista, no tabla

    product_id = fields.Many2one('product.template', string='Producto')
    purchased_month_to_date = fields.Float(string='Comprado mes')
    budget_month = fields.Float(string='Presupuesto mes')
    purchased_year_to_date = fields.Float(string='Comprado año')
    budget_year = fields.Float(string='Presupuesto año')


    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE OR REPLACE VIEW %s AS (
          SELECT
          pt.id AS template_id,
          pt.name AS template_name,
          
          -- Total de pallets del mes actual
          COALESCE(SUM(CASE
              WHEN date_trunc('month', po.date_order) = date_trunc('month', CURRENT_DATE)
              THEN pol.pallets ELSE 0 END), 0) AS pallets_mes_actual,

          -- Total de pallets del año actual
          COALESCE(SUM(CASE
              WHEN date_trunc('year', po.date_order) = date_trunc('year', CURRENT_DATE)
              THEN pol.pallets ELSE 0 END), 0) AS pallets_ano_actual

          FROM purchase_order_line pol
          JOIN purchase_order po ON po.id = pol.order_id
          JOIN product_product pp ON pp.id = pol.product_id
          JOIN product_template pt ON pt.id = pp.product_tmpl_id

          WHERE po.state IN ('purchase', 'done')  -- Consideramos solo órdenes confirmadas

          GROUP BY pt.id, pt.name
          HAVING
            COALESCE(SUM(CASE
                WHEN date_trunc('month', po.date_order) = date_trunc('month', CURRENT_DATE)
                THEN pol.pallets ELSE 0 END), 0) > 0
            OR
            COALESCE(SUM(CASE
                WHEN date_trunc('year', po.date_order) = date_trunc('year', CURRENT_DATE)
                THEN pol.pallets ELSE 0 END), 0) > 0
                            )""" % (self._table))


