# coding: utf-8

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    class SaleOrderReport(models.AbstractModel):
        _name = 'report.anavale.report_saleorder_no_amounts'
        _description = 'Sale order Report'

        def _get_report_values(self, docids, data=None):

            docs = self.env['sale.order'].browse(docids)

            values = {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'proforma': True
            }
            pickings = docs.mapped('picking_ids')
            if len(pickings)>0:
                pickings_ids = pickings.filtered(lambda p: p.state != 'cancel')
                for picking in pickings_ids:
                    picking.custom_state_delivery = 'assigned'
            return values