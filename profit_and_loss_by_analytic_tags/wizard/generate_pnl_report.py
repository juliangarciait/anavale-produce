# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class ProfitNLossWizard(models.TransientModel): 
    _name = 'profit.loss.wizard'

    start_date = fields.Date(default=fields.Date.context_today)
    end_date = fields.Date(default=fields.Date.context_today)
    filter_by = fields.Selection([('product', 'Product'),
        ('lot', 'Lot'),
        ('supplier', 'Supplier'),
        ('lot_by_supplier', 'Lot by supplier')])
    tag_ids = fields.Many2many("account.analytic.tag")
    partner_id = fields.Many2one("res.partner")
    tag_domain_ids = fields.Many2many("account.analytic.tag", "tag_domain_rel")
    text_lot = fields.Char()


    @api.onchange("start_date", "end_date", "filter_by", "text_lot")
    def change_range_date_get_tags(self):
        tag_domain_ids = []
        if self.filter_by == "product":
            self._cr.execute("select id from account_analytic_tag where name similar to 'P([0-9]*[.])?[0-9]+';")
            tag_ids = self._cr.fetchall()
            for tag in tag_ids:
                tag_domain_ids.append(tag[0])
        if self.filter_by == "supplier":
            self._cr.execute("select id from account_analytic_tag where name similar to '[A-Z]+';")
            tag_ids = self._cr.fetchall()
            for tag in tag_ids:
                tag_domain_ids.append(tag[0])
        if self.filter_by == "lot":
            self._cr.execute("select id from account_analytic_tag where name similar to '[A-Z]+\d+-\d+';")
            tag_ids = self._cr.fetchall()
            for tag in tag_ids:
                tag_domain_ids.append(tag[0])
        if self.filter_by == "lot_by_supplier":
            self._cr.execute("select id,name from account_analytic_tag where name similar to '[A-Z]+\d+-\d+';")
            tag_ids = self._cr.fetchall()
            for tag in tag_ids:
                if self.text_lot and self.text_lot in tag[1]:
                    tag_domain_ids.append(tag[0])
        query_tags = """
select DISTINCT tag.account_analytic_tag_id as id from account_analytic_tag_account_move_line_rel as tag where tag.account_move_line_id in (select id from account_move_line where date <= '%s' and date >= '%s')
        """ % (self.end_date, self.start_date)
        if tag_domain_ids:
            if len(tag_domain_ids) == 1:
                query_tags += "  and tag.account_analytic_tag_id = %s"
                query_tags = query_tags%(tag_domain_ids[0])
            else:
                query_tags += "  and tag.account_analytic_tag_id in %s"
                query_tags = query_tags%(tuple(tag_domain_ids),)
        self._cr.execute(query_tags)
        tag_to_domain = self._cr.dictfetchall()
        self.tag_domain_ids = [tag.get("id") for tag in tag_to_domain]
        self.tag_ids = [tag.get("id") for tag in tag_to_domain]


    def gen_report(self):
        report = self.env.ref("profit_and_loss_by_analytic_tags.pnl_excel")
        action = report.report_action(self)
        return action
