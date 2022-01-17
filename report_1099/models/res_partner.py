# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd.
# Copyright (C) 2019 (https://www.bistasolutions.com)
#
##############################################################################

# import re

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def return_report_1099_report_config(self):
        """
        Method will call from q-web report to check and return partner's
        report 1099 record which configured.
        """
        rep_1099_conf_rec = \
            self.env['report.1099.config.partner'].search(
                                              [('partner_id', '=', self.id)],
                                              limit=1)
        return rep_1099_conf_rec
