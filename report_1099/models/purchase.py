# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd.
# Copyright (C) 2019 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_account_move_line(self, move):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        if move.partner_id:
            repo_1099_obj = self.env['report.1099.config.partner']
            rep_1099_conf_rec = repo_1099_obj.search(
                                 [('partner_id', '=', move.partner_id.id)],
                                 limit=1)
            if rep_1099_conf_rec and rep_1099_conf_rec.is_1099:
                res.update({'is_1099': rep_1099_conf_rec.is_1099,
                            'type_income': rep_1099_conf_rec.type_income})
        return res
