from odoo import api, fields, models, tools

class BudgetReport(models.Model):
    _name = 'report.budget.purchase'
    _description = 'Reporte Presupuesto vs Compras'
    _auto = False  # importante: porque es una vista, no tabla

    product_id = fields.Many2one('product.template', string='Producto')
    purchased_month_to_date = fields.Float(string='Comprado mes')
    budget_month = fields.Float(string='Presupuesto mes')
    purchased_year_to_date = fields.Float(string='Comprado año')
    budget_year = fields.Float(string='Presupuesto año')


    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT
        row_number() OVER () AS id,
        pt.id AS product_id,
        
        -- Presupuesto mensual
        COALESCE(bm.budget_month, 0.0) AS budget_month,
        
        -- Presupuesto año a la fecha
        COALESCE(by.budget_year, 0.0) AS budget_year,

        -- Compras mes a la fecha
        COALESCE(pm.purchased_month_to_date, 0.0) AS purchased_month_to_date,

        -- Compras año a la fecha
        COALESCE(py.purchased_year_to_date, 0.0) AS purchased_year_to_date

    FROM product_template pt

    -- Subconsulta: presupuesto mensual
    LEFT JOIN (
        SELECT product_id, SUM(quantity) AS budget_month
        FROM purchase_budget
        WHERE date_budget >= date_trunc('month', CURRENT_DATE)
          AND date_budget <= CURRENT_DATE
        GROUP BY product_id
    ) bm ON bm.product_id = pt.id

    -- Subconsulta: presupuesto anual
    LEFT JOIN (
        SELECT product_id, SUM(quantity) AS budget_year
        FROM purchase_budget
        WHERE date_budget >= date_trunc('year', CURRENT_DATE)
          AND date_budget <= CURRENT_DATE
        GROUP BY product_id
    ) by ON by.product_id = pt.id

    -- Subconsulta: compras del mes
    LEFT JOIN (
        SELECT pp.product_tmpl_id AS product_tmpl_id, SUM(pol.qty_received) AS purchased_month_to_date
        FROM purchase_order_line pol
        JOIN purchase_order po ON po.id = pol.order_id
        JOIN product_product pp ON pol.product_id = pp.id
        WHERE po.state IN ('purchase', 'done')
          AND po.date_order >= date_trunc('month', CURRENT_DATE)
          AND po.date_order <= CURRENT_DATE
        GROUP BY pp.product_tmpl_id
    ) pm ON pm.product_tmpl_id = pt.id

    -- Subconsulta: compras del año
    LEFT JOIN (
        SELECT pp.product_tmpl_id AS product_tmpl_id, SUM(pol.qty_received) AS purchased_year_to_date
        FROM purchase_order_line pol
        JOIN purchase_order po ON po.id = pol.order_id
        JOIN product_product pp ON pol.product_id = pp.id
        WHERE po.state IN ('purchase', 'done')
          AND po.date_order >= date_trunc('year', CURRENT_DATE)
          AND po.date_order <= CURRENT_DATE
        GROUP BY pp.product_tmpl_id
    ) py ON py.product_tmpl_id = pt.id

    -- Filtrar productos sin datos
    WHERE 
        COALESCE(bm.budget_month, 0) > 0
     OR COALESCE(by.budget_year, 0) > 0
     OR COALESCE(pm.purchased_month_to_date, 0) > 0
     OR COALESCE(py.purchased_year_to_date, 0) > 0
            )""" % (self._table))


