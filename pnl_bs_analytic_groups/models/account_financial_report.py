# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import copy
import ast

from odoo import models, fields, api, _



class ReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"
    
    @api.model
    def _get_options(self, previous_options=None):
        rslt = super(ReportAccountFinancialReport, self)._get_options(previous_options)
        
        if previous_options and previous_options.get('analytic_group'):
            rslt['analytic_group'] = True
        return rslt



    def _get_lines(self, options, line_id=None):
        if options and 'analytic_accounts' in options and options.get('analytic_accounts') and 'analytic_group' in options and options.get('analytic_group'):
            if 'groups' in options:
                if 'fields' in options.get('groups') and 'analytic_account_id' not in options.get('groups')['fields']:
                    options.get('groups')['fields'].append('analytic_account_id')
                    options['groups']['ids'] = self._get_groups([], ['analytic_account_id'])
                else:
                    options.get('groups')['fields'] = ['analytic_account_id']
                    options['groups']['ids'] = self._get_groups([], ['analytic_account_id'])
            else:
                options['groups'] = {}
                options['groups']['fields'] = ['analytic_account_id']
                options['groups']['ids'] = self._get_groups([('analytic_account_id','in',options.get('analytic_accounts'))], ['analytic_account_id'])
        return super(ReportAccountFinancialReport, self)._get_lines(options,line_id)



