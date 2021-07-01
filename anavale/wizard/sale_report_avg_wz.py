# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time, datetime

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class SaleReportAvg(models.TransientModel):
    _name = 'sale.report.avg.wizard'
    _description = 'Sale Reporte AVG Wz'

    report_type = fields.Selection(
        string='Report type',
        selection=[('lot', 'By Lot')],
        default='lot')

    from_date = fields.Date('From', default=time.strftime('%Y-01-01'))
    to_date = fields.Date('To', default=time.strftime('%Y-12-31'))

    def action_open_window(self):
        self.ensure_one()
        context = dict(self.env.context or {})

        def ref(module, xml_id):
            proxy = self.env['ir.model.data']
            return proxy.get_object_reference(module, xml_id)

        if self.report_type == 'product':
            report_name = 'Sale Report By Product'
            model_search = 'sale.report.avg'
            model, tree_view_id = ref('anavale', 'view_sale_report_avg_tree')
        else:
            report_name = 'Sale Report By Lot'
            model_search = 'sale.report.by.lot'
            model, tree_view_id = ref('anavale', 'view_sale_report_by_lot_tree')

        # context.update(invoice_state=self.invoice_state)

        if self.from_date:
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            date_from1 = str(self.from_date) +" 00:00:00"
            date_from1 = datetime.datetime.strptime(date_from1, DATETIME_FORMAT)
            #date_from1 = date_from1 - datetime.timedelta(hours=5)
            context.update(date_from=date_from1)
            #context.update(date_from=self.from_date)

        if self.to_date:
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            date_to1 = str(self.to_date) +" 23:59:59"
            date_to1 = datetime.datetime.strptime(date_to1, DATETIME_FORMAT)
            #date_to1 = date_to1 + datetime.timedelta(hours=19)
            context.update(date_to=date_to1)
            #context.update(date_to=self.to_date)

        self.env[model_search].with_context(context).init()

        views = [
            (tree_view_id, 'tree')
        ]
        return {
            'name': report_name,
            'context': context,
            "view_mode": 'tree,form',
            'res_model': model_search,
            'type': 'ir.actions.act_window',
            'views': views,
            'view_id': False
        }
