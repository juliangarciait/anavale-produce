# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _name = "commision.report"
    _description = "Reporte de comisiones"
    _auto = False
    #_rec_name = 'date'
    #_order = 'date desc'

    @api.model
    def _get_done_states(self):
        return ['sale', 'done', 'paid']
    

    payment_id = fields.Many2one('account.payment', 'Payment', readonly=True)
    payment_amount = fields.Float(string='Cant. Pagada')
    payment_date = fields.Date(string='Fecha pagado', related='payment_id.payment_date')
    invoice_id = fields.Many2one('account.move', 'Factura', readonly=True)
    invoice_date = fields.Date(string='Fecha factura', related='invoice_id.date')
    ventas_cobradas = fields.Float('Invoice pagado', readonly=True)
    vendedor_id = fields.Many2one('res.partner', 'Vendedor', readonly=True)
    cliente_id = fields.Many2one('res.partner', 'Cliente', readonly=True) 
    comision = fields.Float('Comision', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """ ap.id as id, ap.id as payment_id,ap.amount as payment_amount, 
        amlb.move_id as invoice_id, amlb.date as invoice_date, apr.amount as ventas_cobradas, 
        rpu.id as vendedor_id, rpaa.id as cliente_id, (apr.amount*.005) as comision """

        for field in fields.values():
            select_ += field

        from_ = """
                account_payment as ap join res_partner as rpaa on ap.partner_id = rpaa.id join 
                (select account_move.id, account_move.name, 
                account_move.date, account_move_line.id as idd, account_move_line.move_id, account_move_line.move_name,
                account_move_line.account_internal_type
                from account_move join account_move_line 
                on account_move.id = account_move_line.move_id where account_move_line.account_internal_type = 'receivable' ) as aml
                on ap.move_name = aml.name join account_partial_reconcile as apr
                on aml.idd = apr.credit_move_id join account_move_line as amlb
                on apr.debit_move_id = amlb.id
                join res_partner as rp on amlb.partner_id = rp.id
                left join res_users as ru on rp.user_id = ru.id
                left join res_partner as rpu on ru.partner_id = rpu.id
                %s
        """ % from_clause

        groupby_ = """
             %s
        """ % (groupby)

        return """%s (SELECT %s FROM %s WHERE amlb.date > '2024-12-31' )""" % (with_, select_, from_)

    def init(self):
        self._table = 'commision_report'
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

