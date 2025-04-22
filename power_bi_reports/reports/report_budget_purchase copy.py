from odoo import api, fields, models, tools

class DueReport(models.Model):
    _name = 'report.customer.due'
    _description = 'Reporte Deuda de clientes'
    _auto = False  # importante: porque es una vista, no tabla

    partner_id = fields.Many2one('res.partner', string='Customer')
    total_due = fields.Float(string='Deuda total')
    budget_month = fields.Float(string='Presupuesto mes')
    purchased_year_to_date = fields.Float(string='Comprado año')
    budget_year = fields.Float(string='Presupuesto año')


    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT
        row_number() OVER () AS id,
        rp.id AS partner_id,

        -- Total adeudado (en valor absoluto)
        COALESCE(SUM(CASE
            WHEN aat.type IN ('receivable', 'payable')
                 AND aml.amount_residual != 0
            THEN aml.amount_residual END), 0.0) AS total_due,

        -- Total vencido
        COALESCE(SUM(CASE
            WHEN aat.type IN ('receivable', 'payable')
                 AND aml.amount_residual != 0
                 AND (aml.date_maturity < CURRENT_DATE or aml.date_maturity is NULL )
            THEN aml.amount_residual END), 0.0) AS over_due,

        -- Último pago
        (
            SELECT MAX(ap.payment_date)
            FROM account_payment ap
            WHERE ap.partner_id = rp.id
              AND ap.state = 'posted'
        ) AS last_payment

    FROM res_partner rp

    LEFT JOIN account_move_line aml ON aml.partner_id = rp.id
    LEFT JOIN account_account aa ON aml.account_id = aa.id
    LEFT JOIN account_account_type aat ON aa.user_type_id = aat.id

    WHERE
        aml.parent_state = 'posted'
        AND aml.company_id IS NOT NULL

    GROUP BY rp.id

    HAVING 
        COALESCE(SUM(CASE
            WHEN aat.type IN ('receivable', 'payable')
                 AND aml.amount_residual != 0
            THEN aml.amount_residual END), 0.0) > 0
            )""" % (self._table))


