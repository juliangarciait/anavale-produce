# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _


class SaleReportAvg(models.TransientModel):
    _name = 'sale.report.avg.wizard'
    _description = 'Sale Reporte AVG Wz'

    from_date = fields.Date('From', default=time.strftime('%Y-01-01'))
    to_date = fields.Date('To', default=time.strftime('%Y-12-31'))

    def action_open_window(self):
        self.ensure_one()
        context = dict(self.env.context or {})

        def ref(module, xml_id):
            proxy = self.env['ir.model.data']
            return proxy.get_object_reference(module, xml_id)

        model, tree_view_id = ref('anavale', 'view_sale_report_avg_tree')

        #context.update(invoice_state=self.invoice_state)

        #if self.from_date:
        #    context.update(date_from=self.from_date)

        #if self.to_date:
        #    context.update(date_to=self.to_date)

        views = [
            (tree_view_id, 'tree')
        ]
        return {
            'name': _('Product Margins'),
            'context': context,
            "view_mode": 'tree,form',
            'res_model': 'sale.report.avg',
            'type': 'ir.actions.act_window',
            'views': views,
            'view_id': False
        }
