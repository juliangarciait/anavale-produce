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
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero, ustr
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class ReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"
    
    @api.model
    def _get_options(self, previous_options=None):
        rslt = super(ReportAccountFinancialReport, self)._get_options(previous_options)
        if previous_options and previous_options.get('analytic_tag'):
            rslt['analytic_tag'] = True
        return rslt

    def _get_lines(self, options, line_id=None):
        if options and 'analytic_tags' in options and options.get('analytic_tags') and 'analytic_tag' in options and options.get('analytic_tag'):
            if 'groups' in options:
                if 'fields' in options.get('groups') and 'analytic_tag_ids' not in options.get('groups')['fields']:
                    options.get('groups')['fields'].append('analytic_tag_ids')
                    options['groups']['ids'] = self._get_groups_account([], ['analytic_tag_ids'],options.get('analytic_tags'))
                else:
                    options.get('groups')['fields'] = ['analytic_tag_ids']
                    options['groups']['ids'] = self._get_groups_account([], ['analytic_tag_ids'],options.get('analytic_tags'))
            else:
                options['groups'] = {}
                options['groups']['fields'] = ['analytic_tag_ids']
                options['groups']['ids'] = self._get_groups_account([('analytic_tag_ids','in',options.get('analytic_tags'))], ['analytic_tag_ids'],options.get('analytic_tags'))
        return super(ReportAccountFinancialReport, self)._get_lines(options,line_id)

    def _get_groups_account(self, domain, group_by,data):
        analytic_tags = []
        for d in data:
            if d:
                analytic_tags.append((d,))
        return analytic_tags

class FormulaContext(dict):
    def __init__(self, reportLineObj, linesDict, currency_table, financial_report, curObj=None, only_sum=False, *data):
        self.reportLineObj = reportLineObj
        self.curObj = curObj
        self.linesDict = linesDict
        self.currency_table = currency_table
        self.only_sum = only_sum
        self.financial_report = financial_report
        return super(FormulaContext, self).__init__(data)

    def __getitem__(self, item):
        formula_items = ['sum', 'sum_if_pos', 'sum_if_neg']
        if item in set(__builtins__.keys()) - set(formula_items):
            return super(FormulaContext, self).__getitem__(item)

        if self.only_sum and item not in formula_items:
            return FormulaLine(self.curObj, self.currency_table, self.financial_report, type='null')
        if self.get(item):
            return super(FormulaContext, self).__getitem__(item)
        if self.linesDict.get(item):
            return self.linesDict[item]
        if item == 'sum':
            res = FormulaLine(self.curObj, self.currency_table, self.financial_report, type='sum')
            self['sum'] = res
            return res
        if item == 'sum_if_pos':
            res = FormulaLine(self.curObj, self.currency_table, self.financial_report, type='sum_if_pos')
            self['sum_if_pos'] = res
            return res
        if item == 'sum_if_neg':
            res = FormulaLine(self.curObj, self.currency_table, self.financial_report, type='sum_if_neg')
            self['sum_if_neg'] = res
            return res
        if item == 'NDays':
            d1 = fields.Date.from_string(self.curObj.env.context['date_from'])
            d2 = fields.Date.from_string(self.curObj.env.context['date_to'])
            res = (d2 - d1).days
            self['NDays'] = res
            return res
        if item == 'count_rows':
            return self.curObj._get_rows_count()
        if item == 'from_context':
            return self.curObj._get_value_from_context()
        line_id = self.reportLineObj.search([('code', '=', item)], limit=1)
        if line_id:
            date_from, date_to, strict_range = line_id._compute_date_range()
            res = FormulaLine(line_id.with_context(strict_range=strict_range, date_from=date_from, date_to=date_to), self.currency_table, self.financial_report, linesDict=self.linesDict)
            self.linesDict[item] = res
            return res
        return super(FormulaContext, self).__getitem__(item)
              
class FormulaLine(object):
    def __init__(self, obj, currency_table, financial_report, type='balance', linesDict=None):
        if linesDict is None:
            linesDict = {}
        fields = dict((fn, 0.0) for fn in ['debit', 'credit', 'balance'])
        if type == 'balance':
            fields = obj._get_balance(linesDict, currency_table, financial_report)[0]
            linesDict[obj.code] = self
        elif type in ['sum', 'sum_if_pos', 'sum_if_neg']:
            if type == 'sum_if_neg':
                obj = obj.with_context(sum_if_neg=True)
            if type == 'sum_if_pos':
                obj = obj.with_context(sum_if_pos=True)
            if obj._name == 'account.financial.html.report.line':
                fields = obj._get_sum(currency_table, financial_report)
                self.amount_residual = fields['amount_residual']
            elif obj._name == 'account.move.line':
                self.amount_residual = 0.0
                field_names = ['debit', 'credit', 'balance', 'amount_residual']
                res = obj.env['account.financial.html.report.line']._compute_line(currency_table, financial_report)
                for field in field_names:
                    fields[field] = res[field]
                self.amount_residual = fields['amount_residual']
        elif type == 'not_computed':
            for field in fields:
                fields[field] = obj.get(field, 0)
            self.amount_residual = obj.get('amount_residual', 0)
        elif type == 'null':
            self.amount_residual = 0.0
        self.balance = fields['balance']
        self.credit = fields['credit']
        self.debit = fields['debit']

class AccountFinancialReportLineInherit(models.Model):
    _inherit = "account.financial.html.report.line"

    def _eval_formula(self, financial_report, debit_credit, currency_table, linesDict_per_group, groups=False):
        groups = groups or {'fields': [], 'ids': [()]}
        debit_credit = debit_credit and financial_report.debit_credit
        formulas = self._split_formulas()
        currency = self.env.company.currency_id
        line_res_per_group = []

        if not groups['ids']:
            return [{'line': {'balance': 0.0}}]

        # this computes the results of the line itself
        for group_index, group in enumerate(groups['ids']):
            self_for_group = self.with_context(group_domain=self._get_group_domain(group, groups))
            linesDict = linesDict_per_group[group_index]
            line = False

            if self.code and self.code in linesDict:
                line = linesDict[self.code]
            elif formulas and formulas['balance'].strip() == 'count_rows' and self.groupby:
                line_res_per_group.append({'line': {'balance': self_for_group._get_rows_count()}})
            elif formulas and formulas['balance'].strip() == 'from_context':
                line_res_per_group.append({'line': {'balance': self_for_group._get_value_from_context()}})
            else:
                line = FormulaLine(self_for_group, currency_table, financial_report, linesDict=linesDict)

            if line:
                res = {}
                res['balance'] = line.balance
                res['balance'] = currency.round(line.balance) if self.figure_type != 'percents' else line.balance
                if debit_credit:
                    
                    res['credit'] = currency.round(line.credit)
                    res['debit'] = currency.round(line.debit)
                line_res_per_group.append(res)

        # don't need any groupby lines for count_rows and from_context formulas
        if all('line' in val for val in line_res_per_group):
            return line_res_per_group

        columns = []
        # this computes children lines in case the groupby field is set
        if self.domain and self.groupby and self.show_domain != 'never':
            if self.groupby not in self.env['account.move.line']:
                raise ValueError(_('Groupby should be a field from account.move.line'))

            groupby = [self.groupby or 'id']
            if groups:
                groupby = groups['fields'] + groupby
            groupby = ', '.join(['"account_move_line".%s' % field for field in groupby])

            aml_obj = self.env['account.move.line']
            tables, where_clause, where_params = aml_obj._query_get(domain=self._get_aml_domain())
            if financial_report.tax_report:
                where_clause += ''' AND "account_move_line".tax_exigible = 't' '''

            select, params = self._query_get_select_sum(currency_table)
            params += where_params

            sql, params = self._build_query_eval_formula(groupby, select, tables, where_clause, params)
            
            account_id = self._context.get('analytic_account_ids')
            tag_id = self._context.get('analytic_tag_ids')
            if tag_id  and account_id:
                raise UserError(_('Please select either Analytic Groups or Analytic Tags. both together is not supported!'))
            if account_id and not tag_id:
                self.env.cr.execute(sql, params)
                results = self.env.cr.fetchall()
                for group_index, group in enumerate(groups['ids']):
                    linesDict = linesDict_per_group[group_index]
                    results_for_group = [result for result in results if group == result[:len(group)]]
                    if results_for_group:
                        results_for_group = [r[len(group):] for r in results_for_group]
                        results_for_group = dict([(k[0], {'balance': k[1], 'amount_residual': k[2], 'debit': k[3], 'credit': k[4]}) for k in results_for_group])
                        c = FormulaContext(self.env['account.financial.html.report.line'].with_context(group_domain=self._get_group_domain(group, groups)),
                                           linesDict, currency_table, financial_report, only_sum=True)
                        if formulas:
                            for key in results_for_group:
                                c['sum'] = FormulaLine(results_for_group[key], currency_table, financial_report, type='not_computed')
                                c['sum_if_pos'] = FormulaLine(results_for_group[key]['balance'] >= 0.0 and results_for_group[key] or {'balance': 0.0},
                                                              currency_table, financial_report, type='not_computed')
                                c['sum_if_neg'] = FormulaLine(results_for_group[key]['balance'] <= 0.0 and results_for_group[key] or {'balance': 0.0},
                                                              currency_table, financial_report, type='not_computed')
                                for col, formula in formulas.items():
                                    if col in results_for_group[key]:
                                        results_for_group[key][col] = safe_eval(formula, c, nocopy=True)
                        to_del = []
                        for key in results_for_group:
                            if self.env.company.currency_id.is_zero(results_for_group[key]['balance']):
                                to_del.append(key)
                        for key in to_del:
                            del results_for_group[key]

                        results_for_group.update({'line': line_res_per_group[group_index]})
                        columns.append(results_for_group)
                    else:
                        res_vals = {'balance': 0.0}
                        if debit_credit:
                            res_vals.update({'debit': 0.0, 'credit': 0.0})
                        columns.append({'line': res_vals})

            elif tag_id and not account_id:
                total_credit_amount = 0
                if tag_id:
                    for tag in tag_id:
                        tag_line = self.env['account.move.line'].sudo().search([('analytic_tag_ids',"=",tag.id)])
                        for credit_amount in tag_line:
                            total_credit_amount += credit_amount.credit

                total_debit_amount = 0
                if tag_id:
                    for tag in tag_id:
                        tag_line = self.env['account.move.line'].sudo().search([('analytic_tag_ids',"=",tag.id)])
                        for debit_amount in tag_line:
                            total_debit_amount += debit_amount.debit

                total_residual_amount = 0
                if tag_id:
                    for tag in tag_id:
                        tag_line = self.env['account.move.line'].sudo().search([('analytic_tag_ids',"=",tag.id)])
                        for residual_amount in tag_line:
                            total_residual_amount += residual_amount.amount_residual

                total_balance = 0
                if tag_id:
                    for tag in tag_id:
                        balance = self.env['account.move.line'].sudo().search([('analytic_tag_ids',"=",tag.id)])
                        for blc in balance:
                            total_balance += blc.balance

                tag_ids = []
                for tag_id in groups['ids']:
                    if tag_id:
                        data =str(tag_id).replace('(','').replace(')','').replace(',','')
                        tag_ids.append(int(data))

                test = tuple(tag_ids) + (36, total_balance, total_residual_amount, total_debit_amount, total_credit_amount)
                results = [test]
               
                for group_index, group in enumerate(groups['ids']):
                    linesDict = linesDict_per_group[group_index]
                    results_for_group = [result for result in results if group == result[:len(group)]]
                    if results_for_group:
                        results_for_group = [r[len(group):] for r in results_for_group]
                        results_for_group = dict([(k[0], {'balance': k[1], 'amount_residual': k[2], 'debit': k[3], 'credit': k[4]}) for k in results_for_group])
                        c = FormulaContext(self.env['account.financial.html.report.line'].with_context(group_domain=self._get_group_domain(group, groups)),
                                           linesDict, currency_table, financial_report, only_sum=True)
                        if formulas:
                            for key in results_for_group:
                                c['sum'] = FormulaLine(results_for_group[key], currency_table, financial_report, type='not_computed')
                                c['sum_if_pos'] = FormulaLine(results_for_group[key]['balance'] >= 0.0 and results_for_group[key] or {'balance': 0.0},
                                                              currency_table, financial_report, type='not_computed')
                                c['sum_if_neg'] = FormulaLine(results_for_group[key]['balance'] <= 0.0 and results_for_group[key] or {'balance': 0.0},
                                                              currency_table, financial_report, type='not_computed')
                                for col, formula in formulas.items():
                                    if col in results_for_group[key]:
                                        results_for_group[key][col] = safe_eval(formula, c, nocopy=True)
                        to_del = []
                        for key in results_for_group:
                            if self.env.company.currency_id.is_zero(results_for_group[key]['balance']):
                                to_del.append(key)
                        for key in to_del:
                            del results_for_group[key]
                        results_for_group.update({'line': line_res_per_group[group_index]})
                        columns.append(results_for_group)
                    else:
                        res_vals = {'balance': 0.0}
                        if debit_credit:
                            res_vals.update({'debit': 0.0, 'credit': 0.0})
                        columns.append({'line':  line_res_per_group[group_index]})
            
        return columns or [{'line': res} for res in line_res_per_group]
