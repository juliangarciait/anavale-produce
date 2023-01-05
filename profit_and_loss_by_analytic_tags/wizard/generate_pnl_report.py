# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class ProfitNLossWizard(models.TransientModel): 
    _name = 'profit.loss.wizard'

    start_date = fields.Date(default=fields.Date.context_today)
    end_date = fields.Date(default=fields.Date.context_today)
    tag_ids = fields.Many2many("account.analytic.tag")


    def gen_report(self):
        report = self.env.ref("profit_and_loss_by_analytic_tags.pnl_excel")
        action = report.report_action(self)
        return action