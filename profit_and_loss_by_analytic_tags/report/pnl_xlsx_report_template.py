# -*- encoding: utf-8 -*-

import time
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError
from xlsxwriter.utility import xl_rowcol_to_cell
from datetime import datetime
from mergedeep import merge

import logging 
_logger = logging.getLogger(__name__)

class XlsxReport(models.AbstractModel): 
    _name = 'report.profit_and_loss_by_analytic_tags.pnl_excel'
    _inherit = 'report.odoo_report_xlsx.abstract'

    def get_domain_query_not_tag(self, type_account, obj_wizard):
        domain = "WHERE "
        if type_account == 13:
            domain += "account.user_type_id = 13"
        if type_account == 14:
            domain += "account.user_type_id = 14"
        if type_account == 15:
            domain += "account.user_type_id = 15"
        if type_account == 16:
            domain += "account.user_type_id = 16"
        if type_account == 17:
            domain += "account.user_type_id = 17"
        if obj_wizard.start_date and obj_wizard.end_date:
            domain += " AND aml.date >= '%s' AND aml.date <= '%s'"%(obj_wizard.start_date, obj_wizard.end_date)
        domain += " AND am.state = 'posted'"
        return domain

    def get_domain_query(self, type_account, obj_wizard):
        domain = "WHERE "
        if type_account == 13:
            domain += "account.user_type_id = 13"
        if type_account == 14:
            domain += "account.user_type_id = 14"
        if type_account == 15:
            domain += "account.user_type_id = 15"
        if type_account == 16:
            domain += "account.user_type_id = 16"
        if type_account == 17:
            domain += "account.user_type_id = 17"
        if obj_wizard.tag_ids:
            if len(obj_wizard.tag_ids) == 1:
                domain += " AND aat_acl.account_analytic_tag_id = %s"%(str(obj_wizard.tag_ids.id))
            else:
                domain += " AND aat_acl.account_analytic_tag_id in %s"%(str(tuple(obj_wizard.tag_ids.ids)))
        if obj_wizard.start_date and obj_wizard.end_date:
            domain += " AND aml.date >= '%s' AND aml.date <= '%s'"%(obj_wizard.start_date, obj_wizard.end_date)
        domain += " AND am.state = 'posted'"
        return domain
    
    def generate_xlsx_report(self, workbook, data, objects): 
        workbook.set_properties({
            'comments' : 'Profit and loss'
        })
        money_format = workbook.add_format({'num_format': '[$$]#,##0.00'})
        money_format_bold = workbook.add_format({'num_format': '[$$]#,##0.00', 'bold': True})
        bold = workbook.add_format({'bold': True})
        sheet = workbook.add_worksheet(_('Reporte'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(100)
        sheet.set_column(0, 0, 35)
        domain_income = self.get_domain_query(13, objects)
        query_op_income = """
SELECT aat_acl.account_analytic_tag_id as tag_id,at.name as tag_name,account.name as acc_name,account.code as acc_code, sum(aml.balance)* -1 as op_income
FROM account_analytic_tag_account_move_line_rel as aat_acl
JOIN account_move_line as aml 
ON aat_acl.account_move_line_id = aml.id
JOIN account_move as am
ON aml.move_id = am.id
JOIN account_account as account
ON aml.account_id = account.id
JOIN account_analytic_tag as at
ON at.id = aat_acl.account_analytic_tag_id
%s
GROUP BY aat_acl.account_analytic_tag_id,at.name,account.name,account.code ORDER BY aat_acl.account_analytic_tag_id,account.code""" % (domain_income)
        self._cr.execute(query_op_income)
        lines_operating_income = self._cr.dictfetchall()

        query_op_income_no_grouping = """
SELECT account.name as acc_name,account.code as acc_code, sum(aml.balance)* -1 as op_income
FROM account_move_line as aml
JOIN account_move as am
ON aml.move_id = am.id
JOIN account_account as account
ON aml.account_id = account.id
%s
GROUP BY account.name,account.code ORDER BY account.code""" % (self.get_domain_query_not_tag(13, objects))
        self._cr.execute(query_op_income_no_grouping)
        lines_operating_income_no_grouping = self._cr.dictfetchall()
        account_name = {item['acc_code']:item["acc_name"] for item in lines_operating_income}
        sheet.write(1, 0, "Income", bold)
        sheet.write(2, 0, "Gross Profit", bold)
        sheet.write(3, 0, "Operating Income", bold)
        row_title = row_tag = 4
        
        for code, name in account_name.items():
            sheet.write(row_title, 0, "%s %s"%(code,name))
            row_title += 1
        groupby_tag_income = {}
        for line in lines_operating_income:
            account_list = groupby_tag_income.get(line.get("tag_name"), {})
            sum_tag =  groupby_tag_income.get(line.get("tag_name"), {}).get("total", 0)
            sum_tag += line.get("op_income", 0)
            account_list.update({line.get("acc_code"): line.get("op_income", 0), 'total': sum_tag})
            groupby_tag_income[line.get("tag_name")] = account_list
        
        tag_ids = groupby_tag_income.keys()
        tag_index = 1
        list_to_write = []
        for tag, line in groupby_tag_income.items():
            sheet.write(0, tag_index, tag, bold)
            for code,acc_name in account_name.items():
                sheet.write(row_tag, tag_index, line.get(code, 0), money_format)
                list_to_write.append(row_tag)
                row_tag += 1
            row_tag = 4
            tag_index += 1
        for sumatory in list_to_write:
            firts_cell = xl_rowcol_to_cell(sumatory, 1)
            last_cell = xl_rowcol_to_cell(sumatory, tag_index-1)
            cell_string = '=SUM(%s:%s)' % (firts_cell, last_cell)
            sheet.write(sumatory, tag_index, cell_string, money_format)
        sheet.write(0, tag_index, "Sumatoria", bold)# Titulo de sumatoria
        sheet.write(0, tag_index+1, "Otros", bold)# Titulo de Otros
        sheet.write(0, tag_index+2, "Total", bold)# Titulo de Total
        tag_index += 1
        for  line in lines_operating_income_no_grouping:
            if line.get("acc_code") in account_name.keys():
                total_cell = xl_rowcol_to_cell(row_tag, tag_index+1)
                sum_cell = xl_rowcol_to_cell(row_tag, tag_index-1)
                sheet.write(row_tag, tag_index, "=%s-%s" %(total_cell, sum_cell), money_format)
                tag_index += 1
                sheet.write(row_tag, tag_index, line.get("op_income", 0), money_format)
                row_tag += 1
                tag_index -= 1
        row_tag = 4
        sheet.write(row_title, 0, "Operating Revenue", bold)
        row_title += 1

        domain_revenue = self.get_domain_query(17, objects)
        query_op_revenue = """
SELECT aat_acl.account_analytic_tag_id as tag_id,at.name as tag_name, account.name as acc_name,account.code as acc_code,sum(aml.balance) as op_revenue
FROM account_analytic_tag_account_move_line_rel as aat_acl
JOIN account_move_line as aml 
ON aat_acl.account_move_line_id = aml.id
JOIN account_move as am
ON aml.move_id = am.id
JOIN account_account as account
ON aml.account_id = account.id
JOIN account_analytic_tag as at
ON at.id = aat_acl.account_analytic_tag_id
%s
GROUP BY aat_acl.account_analytic_tag_id,at.name,account.name,account.code  ORDER BY aat_acl.account_analytic_tag_id,account.code""" % (domain_revenue)
        self._cr.execute(query_op_revenue)
        lines_op_revenue = self._cr.dictfetchall()

        query_op_revenue_no_grouping = """
SELECT account.name as acc_name,account.code as acc_code, sum(aml.balance) as op_revenue
FROM account_move_line as aml
JOIN account_move as am
ON aml.move_id = am.id
JOIN account_account as account
ON aml.account_id = account.id
%s
GROUP BY account.name,account.code ORDER BY account.code""" % (self.get_domain_query_not_tag(17, objects))
        self._cr.execute(query_op_revenue_no_grouping)
        lines_op_revenue_no_grouping = self._cr.dictfetchall()
        account_name = {item['acc_code']:item["acc_name"] for item in lines_op_revenue}
        tag_index = 1
        row_tag = row_title
        row_origin = row_title
        for code, name in account_name.items():
            sheet.write(row_title, 0, "%s %s"%(code,name))
            row_title += 1
        groupby_tag_op_revenue = {}
        for line in lines_op_revenue:
            account_list = groupby_tag_op_revenue.get(line.get("tag_name"), {})
            sum_tag =  groupby_tag_op_revenue.get(line.get("tag_name"), {}).get("total", 0)
            sum_tag += line.get("op_revenue", 0)
            account_list.update({line.get("acc_code"): line.get("op_revenue", 0), 'total': sum_tag})
            groupby_tag_op_revenue[line.get("tag_name")] = account_list
        list_to_write = []
        for tag in tag_ids:
            line = groupby_tag_op_revenue.get(tag, {})
            for code,acc_name in account_name.items():
                sheet.write(row_tag, tag_index, line.get(code, 0), money_format)
                list_to_write.append(row_tag)
                row_tag += 1
            sheet.write(row_tag,tag_index, "=%f-%f"%( groupby_tag_income.get(tag, {}).get("total",0) , groupby_tag_op_revenue.get(tag, {}).get("total",0) ) , money_format_bold)
            list_to_write.append(row_tag)
            row_tag = row_origin
            tag_index += 1
        for sumatory in list_to_write:
            firts_cell = xl_rowcol_to_cell(sumatory, 1)
            last_cell = xl_rowcol_to_cell(sumatory, tag_index-1)
            cell_string = '=SUM(%s:%s)' % (firts_cell, last_cell)
            sheet.write(sumatory, tag_index, cell_string, money_format)
        tag_index += 1
        for  line in lines_op_revenue_no_grouping:
            if line.get("acc_code") in account_name.keys():
                total_cell = xl_rowcol_to_cell(row_tag, tag_index+1)
                sum_cell = xl_rowcol_to_cell(row_tag, tag_index-1)
                sheet.write(row_tag, tag_index, "=%s-%s" %(total_cell, sum_cell), money_format)
                tag_index += 1
                sheet.write(row_tag, tag_index, line.get("op_revenue", 0), money_format)
                row_tag += 1
                tag_index -= 1
        row_tag = 4
        sheet.write(row_title, 0, "Total Cost Revenue", bold)
        row_title += 1
        sheet.write(row_title, 0, "Other Income", bold)
        row_title += 1

        domain_other_income = self.get_domain_query(14, objects)
        query_other_income = """
SELECT aat_acl.account_analytic_tag_id as tag_id,at.name as tag_id,at.name as tag_name, account.name as acc_name,account.code as acc_code, sum(aml.balance)*-1 as other_income
FROM account_analytic_tag_account_move_line_rel as aat_acl
JOIN account_move_line as aml 
ON aat_acl.account_move_line_id = aml.id
JOIN account_move as am
ON aml.move_id = am.id
JOIN account_account as account
ON aml.account_id = account.id
JOIN account_analytic_tag as at
ON at.id = aat_acl.account_analytic_tag_id
%s
GROUP BY aat_acl.account_analytic_tag_id,at.name,account.name,account.code ORDER BY aat_acl.account_analytic_tag_id,account.code""" % (domain_other_income)
        self._cr.execute(query_other_income)
        lines_other_income = self._cr.dictfetchall()

        query_other_income_no_grouping = """
SELECT account.name as acc_name,account.code as acc_code, sum(aml.balance)* -1 as other_income
FROM account_move_line as aml
JOIN account_move as am
ON aml.move_id = am.id
JOIN account_account as account
ON aml.account_id = account.id
%s
GROUP BY account.name,account.code ORDER BY account.code""" % (self.get_domain_query_not_tag(14, objects))
        self._cr.execute(query_other_income_no_grouping)
        lines_other_income_no_grouping = self._cr.dictfetchall()
        account_name = {item['acc_code']:item["acc_name"] for item in lines_other_income}
        tag_index = 1
        row_tag = row_title
        row_origin = row_title
        for code, name in account_name.items():
            sheet.write(row_title, 0, "%s %s"%(code,name))
            row_title += 1
        groupby_tag_other_income = {}
        for line in lines_other_income:
            account_list = groupby_tag_other_income.get(line.get("tag_name"), {})
            sum_tag =  groupby_tag_other_income.get(line.get("tag_name"), {}).get("total", 0)
            sum_tag += line.get("other_income", 0)
            account_list.update({line.get("acc_code"): line.get("other_income", 0), 'total': sum_tag})
            groupby_tag_other_income[line.get("tag_name")] = account_list
        list_to_write = []
        for tag in tag_ids:
            line = groupby_tag_other_income.get(tag, {})
            for code,acc_name in account_name.items():
                sheet.write(row_tag, tag_index, line.get(code, 0), money_format)
                list_to_write.append(row_tag)
                row_tag += 1
            sheet.write(row_tag,tag_index, "=(%f-%f)+%f"%(groupby_tag_income.get(tag, {}).get("total",0), groupby_tag_op_revenue.get(tag, {}).get("total",0), groupby_tag_other_income.get(tag, {}).get("total",0) ) , money_format_bold)
            list_to_write.append(row_tag)
            row_tag = row_origin
            tag_index += 1
        for sumatory in list_to_write:
            firts_cell = xl_rowcol_to_cell(sumatory, 1)
            last_cell = xl_rowcol_to_cell(sumatory, tag_index-1)
            cell_string = '=SUM(%s:%s)' % (firts_cell, last_cell)
            sheet.write(sumatory, tag_index, cell_string, money_format)
        tag_index += 1
        for  line in lines_other_income_no_grouping:
            if line.get("acc_code") in account_name.keys():
                total_cell = xl_rowcol_to_cell(row_tag, tag_index+1)
                sum_cell = xl_rowcol_to_cell(row_tag, tag_index-1)
                sheet.write(row_tag, tag_index, "=%s-%s" %(total_cell, sum_cell), money_format)
                tag_index += 1
                sheet.write(row_tag, tag_index, line.get("other_income", 0), money_format)
                row_tag += 1
                tag_index -= 1
        row_tag = 4
        sheet.write(row_title, 0, "Total Income", bold)
        row_title += 1


        sheet.write(row_title, 0, "Expenses", bold)
        row_title += 1
        sheet.write(row_title, 0, "Expenses", bold)
        row_title += 1

        domain_expense = self.get_domain_query(15, objects)
        query_expense = """
SELECT aat_acl.account_analytic_tag_id as tag_id,at.name as tag_id,at.name as tag_name, account.name as acc_name,account.code as acc_code,sum(aml.balance) as expense
FROM account_analytic_tag_account_move_line_rel as aat_acl
JOIN account_move_line as aml 
ON aat_acl.account_move_line_id = aml.id
JOIN account_move as am
ON aml.move_id = am.id
JOIN account_account as account
ON aml.account_id = account.id
JOIN account_analytic_tag as at
ON at.id = aat_acl.account_analytic_tag_id
%s
GROUP BY aat_acl.account_analytic_tag_id,at.name,account.name,account.code ORDER BY aat_acl.account_analytic_tag_id,account.code""" % (domain_expense)
        self._cr.execute(query_expense)
        lines_expense = self._cr.dictfetchall()
        query_expense_no_grouping = """
SELECT account.name as acc_name,account.code as acc_code, sum(aml.balance) as expense
FROM account_move_line as aml
JOIN account_move as am
ON aml.move_id = am.id
JOIN account_account as account
ON aml.account_id = account.id
%s
GROUP BY account.name,account.code ORDER BY account.code""" % (self.get_domain_query_not_tag(15, objects))
        self._cr.execute(query_expense_no_grouping)
        lines_expense_no_grouping = self._cr.dictfetchall()
        account_name = {item['acc_code']:item["acc_name"] for item in lines_expense}
        tag_index = 1
        row_tag = row_title
        row_origin = row_title
        for code, name in account_name.items():
            sheet.write(row_title, 0, "%s %s"%(code,name))
            row_title += 1
        groupby_tag_expense = {}
        for line in lines_expense:
            account_list = groupby_tag_expense.get(line.get("tag_name"), {})
            sum_tag =  groupby_tag_expense.get(line.get("tag_name"), {}).get("total", 0)
            sum_tag += line.get("expense", 0)
            account_list.update({line.get("acc_code"): line.get("expense", 0), 'total': sum_tag})
            groupby_tag_expense[line.get("tag_name")] = account_list
        list_to_write = []
        for tag in tag_ids:
            line = groupby_tag_expense.get(tag, {})
            for code,acc_name in account_name.items():
                sheet.write(row_tag, tag_index, line.get(code, 0), money_format)
                list_to_write.append(row_tag)
                row_tag += 1
            row_tag = row_origin
            tag_index += 1
        for sumatory in list_to_write:
            firts_cell = xl_rowcol_to_cell(sumatory, 1)
            last_cell = xl_rowcol_to_cell(sumatory, tag_index-1)
            cell_string = '=SUM(%s:%s)' % (firts_cell, last_cell)
            sheet.write(sumatory, tag_index, cell_string, money_format)
        tag_index += 1
        for  line in lines_expense_no_grouping:
            if line.get("acc_code") in account_name.keys():
                total_cell = xl_rowcol_to_cell(row_tag, tag_index+1)
                sum_cell = xl_rowcol_to_cell(row_tag, tag_index-1)
                sheet.write(row_tag, tag_index, "=%s-%s" %(total_cell, sum_cell), money_format)
                tag_index += 1
                sheet.write(row_tag, tag_index, line.get("expense", 0), money_format)
                row_tag += 1
                tag_index -= 1
        row_tag = 4
        sheet.write(row_title, 0, "Depreciation", bold)
        row_title += 1

        domain_depre = self.get_domain_query(16, objects)
        query_depre = """
SELECT aat_acl.account_analytic_tag_id as tag_id,at.name as tag_name, account.name as acc_name,account.code as acc_code, sum(aml.balance) as depreciation
FROM account_analytic_tag_account_move_line_rel as aat_acl
JOIN account_move_line as aml 
ON aat_acl.account_move_line_id = aml.id
JOIN account_move as am
ON aml.move_id = am.id
JOIN account_account as account
ON aml.account_id = account.id
JOIN account_analytic_tag as at
ON at.id = aat_acl.account_analytic_tag_id
%s
GROUP BY aat_acl.account_analytic_tag_id,at.name,account.name,account.code ORDER BY aat_acl.account_analytic_tag_id,account.code""" % (domain_depre)
        self._cr.execute(query_depre)
        lines_depre = self._cr.dictfetchall()
        query_depre_no_grouping = """
SELECT account.name as acc_name,account.code as acc_code, sum(aml.balance) as depreciation
FROM account_move_line as aml
JOIN account_move as am
ON aml.move_id = am.id
JOIN account_account as account
ON aml.account_id = account.id
%s
GROUP BY account.name,account.code ORDER BY account.code""" % (self.get_domain_query_not_tag(16, objects))
        self._cr.execute(query_depre_no_grouping)
        lines_depre_no_grouping = self._cr.dictfetchall()
        account_name = {item['acc_code']:item["acc_name"] for item in lines_depre}
        tag_index = 1
        row_tag = row_title
        row_origin = row_title
        for code, name in account_name.items():
            sheet.write(row_title, 0, "%s %s"%(code,name))
            row_title += 1
        groupby_tag_depre = {}
        for line in lines_depre:
            account_list = groupby_tag_depre.get(line.get("tag_name"), {})
            sum_tag =  groupby_tag_depre.get(line.get("tag_name"), {}).get("total", 0)
            sum_tag += line.get("depreciation", 0)
            account_list.update({line.get("acc_code"): line.get("depreciation", 0), 'total': sum_tag})
            groupby_tag_depre[line.get("tag_name")] = account_list
        list_to_write = []
        for tag in tag_ids:
            line = groupby_tag_depre.get(tag, {})
            for code,acc_name in account_name.items():
                sheet.write(row_tag, tag_index, line.get(code, 0), money_format)
                list_to_write.append(row_tag)
                row_tag += 1
            sheet.write(row_tag,tag_index, "=%f+%f"%( groupby_tag_expense.get(tag, {}).get("total",0), groupby_tag_depre.get(tag, {}).get("total",0) ), money_format_bold)
            list_to_write.append(row_tag)
            tag_index += 1
        for sumatory in list_to_write:
            firts_cell = xl_rowcol_to_cell(sumatory, 1)
            last_cell = xl_rowcol_to_cell(sumatory, tag_index-1)
            cell_string = '=SUM(%s:%s)' % (firts_cell, last_cell)
            sheet.write(sumatory, tag_index, cell_string, money_format)
        tag_index += 1
        for  line in lines_depre_no_grouping:
            if line.get("acc_code") in account_name.keys():
                total_cell = xl_rowcol_to_cell(row_tag, tag_index+1)
                sum_cell = xl_rowcol_to_cell(row_tag, tag_index-1)
                sheet.write(row_tag, tag_index, "=%s-%s" %(total_cell, sum_cell), money_format)
                tag_index += 1
                sheet.write(row_tag, tag_index, line.get("depreciation", 0), money_format)
                row_tag += 1
                tag_index -= 1
        row_tag = 4
        sheet.write(row_title, 0, "Total Expenses", bold)
        row_title += 1
        sheet.write(row_title, 0, "Net Profit", bold)
        row_tag += 1
        tag_index = 1
        for tag in tag_ids:
            sheet.write(row_tag,tag_index, "=(%f-%f)+%f-%f-%f"%(
                groupby_tag_income.get(tag, {}).get("total",0),
                groupby_tag_op_revenue.get(tag, {}).get("total",0),
                groupby_tag_other_income.get(tag, {}).get("total",0),
                groupby_tag_expense.get(tag, {}).get("total",0),
                groupby_tag_depre.get(tag, {}).get("total",0) ), money_format_bold)
            tag_index += 1
