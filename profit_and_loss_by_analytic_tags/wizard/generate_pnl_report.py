# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class ProfitNLossWizard(models.TransientModel): 
    _name = 'profit.loss.wizard'

    start_date = fields.Date(default=fields.Date.context_today)
    end_date = fields.Date(default=fields.Date.context_today)
    tag_ids = fields.Many2many("account.analytic.tag")
    partner_id = fields.Many2one("res.partner")
    partner_ids = fields.Many2many("res.partner")


    @api.onchange("start_date", "end_date")
    def change_range_date_get_partner(self):
        move_ids = self.env["account.move"].search([("date", ">=", self.start_date), ("date", "<=", self.end_date)])
        self.partner_ids = move_ids.mapped(lambda move: move.partner_id)


    def gen_report(self):
        report = self.env.ref("profit_and_loss_by_analytic_tags.pnl_excel")
        action = report.report_action(self)
        return action