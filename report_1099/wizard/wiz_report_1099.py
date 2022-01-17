# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd.
# Copyright (C) 2019 (https://www.bistasolutions.com)
#
##############################################################################

import base64
import io

from odoo.tools.misc import xlwt
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class WizReport1099Download(models.TransientModel):
    _name = 'wiz.report.1099.download'
    _description = 'Report 1099 Download Wizard'

    report_file_name = fields.Char('Name')
    report_file = fields.Binary('File')


class Report1099wiz(models.AbstractModel):
    _name = 'report.report_1099.report_1099_vendor_template'
    _description = 'Report 1099 Vendor Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        data_dict = self.env['wiz.report.1099'].get_report_data(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'report.1099',
            'docs': data_dict,
            'date': str(date.today().year)
        }


class WizReport1099(models.TransientModel):
    _name = 'wiz.report.1099'
    _description = 'Report 1099 Wizard'

    start_date = fields.Date(
        default=lambda self:
        date(date.today().year, 1, 1))
    end_date = fields.Date(
        default=lambda self:
        date(date.today().year, 12, 31))
    report_option = fields.Selection(
        [('show_all', 'Show All'), ('eligible_vendors', 'Eligible Vendors')],
        string='Report Options',
        default='show_all')

    @api.constrains('start_date', 'end_date', 'report_option')
    def check_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_('The start date '
                                        'must be anterior to the end date !'))
            if self.report_option == 'eligible_vendors':
                st_dt = datetime.strptime(str(self.start_date),
                                          DEFAULT_SERVER_DATE_FORMAT)
                en_dt = datetime.strptime(str(self.end_date),
                                          DEFAULT_SERVER_DATE_FORMAT)
                date_dict = self.env.user.company_id. \
                    compute_fiscalyear_dates(st_dt)
                fiscal_st_dt = date_dict.get('date_from', False)
                fiscal_en_dt = date_dict.get('date_to', False)
                if not (st_dt <= fiscal_en_dt and st_dt >= fiscal_st_dt) or \
                        not (en_dt <= fiscal_en_dt and en_dt >= fiscal_st_dt):
                    raise ValidationError(
                        _(" Start / End date should belongs to the same fiscal year !"))

    def print_pdf_report(self):
        report_1099_ids = self._context.get('active_ids', False)
        report_1099_recs = self.env['report.1099'].browse(report_1099_ids)
        return self.env.ref('report_1099.report_1099_vendor'). \
            report_action(report_1099_recs)

    def get_invoices(self):
        """
        Method to create list of records for report 1099 having suitable
        criteria of date and partner.
        """
        rep_1099_data_list = []
        rep_1099_obj = self.env['report.1099']
        payment_obj = self.env['account.payment']
        invoice_obj = self.env['account.move']
        rep_1099_config_obj = self.env['report.1099.config.partner']
        payable_acc = self.env.ref('account.data_account_type_payable')
        final_eligible_dict = {}
        final_invs = []

        # Logic of Eligible Vendors
        if self.report_option == 'eligible_vendors':
            payments_recs = payment_obj.search([
                ('partner_type', '=', 'supplier'),
                ('payment_date', '>=', self.start_date),
                ('payment_date', '<=', self.end_date),
                ('partner_id', '!=', False),
                ('state', 'not in', ('draft', 'cancelled'))
            ])
            pay_eligble_dict = {}
            usd_currency = self.env.ref('base.USD')
            for payment_rec in payments_recs:
                amt = payment_rec.amount
                # Converting Currency if payment made on another currency
                if payment_rec.currency_id != usd_currency:
                    converted_amt = payment_rec.currency_id._convert(
                        payment_rec.amount, usd_currency,
                        payment_rec.company_id, payment_rec.payment_date
                    )
                    amt = converted_amt
                # Preparing dictionary e.g. {partner:payment_amount}
                if payment_rec.payment_type == 'inbound':
                    amt = amt * -1
                if payment_rec.partner_id.id in pay_eligble_dict:
                    existed_amt = pay_eligble_dict[payment_rec.partner_id.id]
                    pay_eligble_dict.update({payment_rec.partner_id.id:
                                             existed_amt + amt})
                else:
                    pay_eligble_dict.update({payment_rec.partner_id.id: amt})

            final_eligible_dict = {
                partner: amount for partner, amount
                in pay_eligble_dict.items() if amount >= 600
            }
            pay_partners = list(final_eligible_dict.keys())
            eligible_dict = {}
            for pay_rec in payments_recs.filtered(lambda p: p.partner_id.id
                                                  in pay_partners):
                line_total = 0.0
                eligible_invs = []
                # checking is_1099 invoice lines and appending that relevant
                # partner,invoice and total to eligible_dict.appending invs.
                # (invoices) as well to remove the duplicated search again.
                for payment_inv in pay_rec.invoice_ids:
                    inv_ln = payment_inv.invoice_line_ids.filtered(
                        lambda r: r.is_1099)
                    line_total += sum(inv_ln.mapped('price_total'))
                    if inv_ln:
                        eligible_invs.append(inv_ln[0].move_id.id)
                # Preparing dictionary e.g.
                # {partner:{'total':line_total,'invs':invoice_list}}
                part_id = pay_rec.partner_id.id
                if part_id in eligible_dict:
                    line_total_amt = eligible_dict[part_id].get('total')
                    existed_invs = eligible_dict[part_id].get('invs')
                    eligible_dict[part_id].update({
                        'total': line_total_amt + line_total,
                        'invs': existed_invs + eligible_invs
                    })
                else:
                    eligible_dict.update({part_id: {'total': line_total,
                                                    'invs': eligible_invs}})
            # Filtering dictionary where payment > 600$.
            for partner, inv_dict in eligible_dict.items():
                if inv_dict.get('total', 0.0) >= 600:
                    final_eligible_dict[partner] = inv_dict['invs']
                    final_invs.extend(inv_dict['invs'])
            invoice_ids = invoice_obj.browse(list(set(final_invs)))
        else:
            # Logic of 'Show all'
            dom = [
                ('invoice_date', '>=', self.start_date),
                ('invoice_date', '<=', self.end_date),
                ('type', 'in', ('in_invoice', 'in_refund')),
                ('state', 'not in', ('draft', 'cancel'))
            ]
            invoice_ids = invoice_obj.search(dom)
        for inv in invoice_ids:
            partner = inv.partner_id
            rep_1099_conf_rec = rep_1099_config_obj.search(
                                       [('partner_id', '=', partner.id)],
                                       limit=1)
            id_no = rep_1099_conf_rec.ein_number
            if rep_1099_conf_rec.ssn_ein == 'ssn':
                id_no = rep_1099_conf_rec.ssn_number
            # using base method finding invoice's payments
            payment_vals = inv._get_reconciled_info_JSON_values()
            # reversing a list of dict.to get latest payment records

            payment_dict_to_show = sorted(payment_vals,
                                          key=lambda k: k['date'],
                                          reverse=True)
            payment_dict = {}
            if payment_dict_to_show:
                payment_rec = payment_obj.browse(
                    payment_dict_to_show[0].get(
                        'account_payment_id',
                        False)
                )
                payment_dict.update({
                    'paid_date': payment_dict_to_show[0].get('date', False),
                    'paid_ref': payment_rec.name,
                    'check_number': payment_rec.check_number,
                    'invoice_state': inv.invoice_payment_state == 'paid' and 'paid' or 'open',
                })
                for inv_line in inv.invoice_line_ids.filtered(
                        lambda r: r.is_1099):
                    amt = inv_line.price_subtotal
                    currency_id = inv_line.currency_id
                    if inv.type == 'in_refund':
                        amt = -inv_line.price_subtotal
                    # at time of partial payment showing amount of
                    # payment instead of invoice line amount
                    if inv.state != 'posted':
                        debit_ttl_amount = 0.0
                        for pay_dict in payment_dict_to_show:
                            debit_ttl_amount += pay_dict.get('amount', 0.0)
                        amt = debit_ttl_amount
                        currency_id = payment_rec.currency_id
                        if inv.type == 'in_refund':
                            amt = -amt
                        debit_line = payment_rec.move_line_ids.filtered(
                            lambda line: line.account_id.
                            user_type_id.id == payable_acc.id)
                        debit_part_id = debit_line.partner_id.id
                        rep_1099_conf_rec = rep_1099_config_obj.search(
                                       [('partner_id', '=', debit_part_id)],
                                       limit=1)
                        debit_line_dict = {
                            'date': inv.invoice_date,
                            'amount': amt,
                            'bill_reference': inv.name,
                            'partner_id': debit_line.partner_id.id,
                            'id_number': id_no,
                            'type_income': rep_1099_conf_rec.type_income,
                            'ssn_ein': rep_1099_conf_rec.ssn_ein,
                            'legal_name': rep_1099_conf_rec.legal_name,
                            'currency_id': debit_line.currency_id and
                            debit_line.currency_id.id or False
                        }
                        debit_line_dict.update(payment_dict)
                        rep_1099_data_list.append(debit_line_dict)
                        break
                    inv_line_dict = {
                        'date': inv.invoice_date,
                        'amount': amt,
                        'bill_reference': inv.name,
                        'partner_id': partner.id,
                        'id_number': id_no,
                        'type_income': inv_line.type_income,
                        'ssn_ein': rep_1099_conf_rec.ssn_ein,
                        'legal_name': rep_1099_conf_rec.legal_name,
                        'invoice_line_id': inv_line.id,
                        'currency_id': currency_id and
                        currency_id.id or False
                    }
                    inv_line_dict.update(payment_dict)
                    rep_1099_data_list.append(inv_line_dict)
        self._cr.execute("delete from report_1099")
        rep_1099_rec = [rep_1099_obj.create(val).id for val
                        in rep_1099_data_list]
        action = self.env.ref('report_1099.action_report_1099')
        result = action.read()[0]
        result['res_id'] = rep_1099_rec
        return result

    def get_report_data(self, docids=False):
        active_ids = self._context.get('active_ids', False)
        if docids:
            active_ids = docids
        cr = self._cr
        cr.execute("""select partner_id,type_income,sum(amount) from
                    report_1099 where id in %s group by partner_id,type_income
                      """, (tuple(active_ids),))
        report_1099_data = cr.dictfetchall()
        data_dict = {}
        report_obj = self.env['res.partner']
        for report_data in report_1099_data:
            if docids:
                partner_rec = report_obj.browse(report_data['partner_id'])
                if partner_rec in data_dict:
                    data_dict[partner_rec].update(
                        {report_data['type_income']: report_data['sum']})
                else:
                    data_dict[partner_rec] = {
                        report_data['type_income']: report_data['sum']}
            else:
                if report_data['partner_id'] in data_dict:
                    data_dict[report_data['partner_id']].update(
                        {report_data['type_income']: report_data['sum']})
                else:
                    data_dict[report_data['partner_id']] = {
                        report_data['type_income']: report_data['sum']}
        return data_dict

    def print_xls_report(self):
        context = dict(self._context)
        if not context:
            context = {}
        filename = 'Report 1099.xls'
        workbook = xlwt.Workbook()
        data_dict = self.get_report_data()
        partner_obj = self.env['res.partner']
        rep_1099_config_obj = self.env['report.1099.config.partner']
        for partner_id, income_dict in data_dict.items():
            partner = partner_obj.browse(partner_id)
            rep_1099_conf_rec = rep_1099_config_obj.search(
                                       [('partner_id', '=', partner.id)],
                                       limit=1)
            partner_name = partner.name if partner.name else ''
            worksheet = workbook.add_sheet(
                'Report 1099 ' + str(partner_name),
                cell_overwrite_ok=True)
            header_bold = xlwt.easyxf(
                "font: bold on; alignment: horiz center;")
            style_wrap = xlwt.easyxf("align: wrap on,vert top;")
            style_bold = xlwt.easyxf(
                "font: bold on,height 250; align: wrap on,horiz right,vert top;")
            style_vert_centre = xlwt.easyxf(
                "font: bold on,height 300; align: wrap on,horiz right,vert center;")
            style_align_right = xlwt.easyxf(
                "font: height 250;align: wrap on,horiz right,vert top;")
            style_center = xlwt.easyxf(
                "alignment: horiz center;align:vert top;")
            style_wrap_2 = xlwt.easyxf("align:vert top;")

            worksheet.col(1).width = 15
            worksheet.col(6).width = 6 * 256
            worksheet.col(11).width = 9 * 256
            worksheet.col(14).width = 2 * 256

            worksheet.write(0, 2, '9595', header_bold)
            worksheet.write(0, 4, 'VOID', header_bold)
            worksheet.write(0, 6, 'CORRECTED', header_bold)

            payers_name_address = ''
            if self.env.user.company_id:
                comp = self.env.user.company_id
                payers_name_address = comp.partner_id._display_address()
            default_str = "PAYER'S name, street address,city or town,state or province, country, ZIP\nor foreign postal code, and telephone no." + (
                "\n" * 3) \
                + payers_name_address

            worksheet.write_merge(1, 12, 0, 5, default_str, style_wrap)

            worksheet.write_merge(1, 4, 6, 8,
                                  '1 Rents ' + '\n\n\n' + '$' + str(
                                      income_dict.get('rent', '')), style_wrap)
            worksheet.write_merge(5, 8, 6, 8,
                                  '2 Royalties' + '\n\n\n' + '$' + str(
                                      income_dict.get('royalty', '')),
                                  style_wrap)
            worksheet.write_merge(9, 12, 6, 8,
                                  '3 Other Income' + '\n\n\n' + '$' + str(
                                      income_dict.get('other', '')),
                                  style_wrap)

            worksheet.write_merge(1, 8, 9, 10,
                                  'OMB No. 1545-0115 \n\n\n' + str(
                                      date.today().year) + '\n\n\n\n\n    Form 1099-MISC',
                                  style_center)
            worksheet.write_merge(1, 8, 11, 14, 'Miscellaneous\nIncome',
                                  style_vert_centre)

            worksheet.write_merge(9, 12, 9, 11,
                                  '4 Federal income tax withheld ' + '\n\n\n' + '$' + str(
                                      income_dict.get(
                                          'federal_income_tax_withheld', '')),
                                  style_wrap)
            worksheet.write_merge(9, 16, 12, 14,
                                  'Copy A \nFor \nInternal Revenue \nService Center \n\nFile with Form 1096.',
                                  style_bold)

            worksheet.write_merge(13, 16, 0, 2,
                                  'PAYER’S federal identification number ',
                                  style_wrap)

            recpnt_no = ''
            if rep_1099_conf_rec and rep_1099_conf_rec.ssn_ein:
                if rep_1099_conf_rec.ssn_ein == 'ein':
                    recpnt_no = rep_1099_conf_rec.ein_number or ''
                if rep_1099_conf_rec.ssn_ein == 'ssn':
                    recpnt_no = rep_1099_conf_rec.ssn_number or ''
            worksheet.write_merge(13, 16, 3, 5,
                                  'RECIPIENT’S identification number' + '\n\n\n' + str(
                                      recpnt_no), style_wrap)

            worksheet.write_merge(13, 16, 6, 8,
                                  '5 Fishing boat proceeds' + '\n\n\n' + '$' + str(
                                      income_dict.get('fishing_boat_proceeds',
                                                      '')), style_wrap)
            worksheet.write_merge(13, 16, 9, 11,
                                  '6 Medical and health care payments' + '\n\n\n' + '$' + str(
                                      income_dict.get(
                                          'medical_and_health_care_payments',
                                          '')), style_wrap_2)

            worksheet.write_merge(17, 20, 0, 5,
                                  'RECIPIENT’S name' + '\n    ' +
                                  str(partner_name),
                                  style_wrap)
            worksheet.write_merge(17, 20, 6, 8,
                                  '7 Nonemployee compensation' + '\n\n\n' + '$' + str(
                                      income_dict.get('non_emp_cmpr', '')),
                                  style_wrap)
            worksheet.write_merge(17, 20, 9, 11,
                                  '8 Substitute payments in lieu of \n   dividends or interest' + '\n\n' + '$' + str(
                                      income_dict.get(
                                          'sub_stitute_payments_in_lieu_of_dividends_or_interest',
                                          '')), style_wrap)

            worksheet.write_merge(17, 32, 12, 14,
                                  'For Privacy Act \nand Paperwork \nReduction Act \nNotice, see the \n2018 General \nInstructions for \nCertain Information \nReturns.',
                                  style_align_right)

            street_address = str(
                partner.street and partner.street or '') + ' ' + str(
                partner.street2 and partner.street2 or '')
            worksheet.write_merge(21, 24, 0, 5,
                                  'Street address (including apt. no.)' +
                                  '\n\n   ' + street_address,
                                  style_wrap)
            worksheet.write_merge(21, 24, 6, 8,
                                  '9 Payer made direct sales of \n   $5,000 or more of consumer \n   products to a buyer \n   (recipient) for resale ▶' + '\n\n' + '$' + str(
                                      income_dict.get(
                                          'sale',
                                          '')), style_wrap)
            worksheet.write_merge(21, 24, 9, 11,
                                  '10 Crop insurance proceeds' + '\n\n\n' + '$' + str(
                                      income_dict.get(
                                          'crop_insurance_proceeds', '')),
                                  style_wrap)

            address = str(partner.city or '') + ' ' + (
                str(partner.state_id.name or '') or '') \
                + ' ' + (str(partner.country_id.name or '') or '') \
                + ' ' + str(partner.zip or '')
            worksheet.write_merge(25, 28, 0, 5,
                                  "City or town, state or province, country, and ZIP or foreign postal code" +
                                  '\n\n   ' + address,
                                  style_wrap)
            worksheet.write_merge(25, 28, 6, 8, '11', style_wrap)
            worksheet.write_merge(25, 28, 9, 11, '12', style_wrap)

            worksheet.write_merge(29, 32, 0, 3,
                                  "Account number (see instructions)",
                                  style_wrap)
            worksheet.write_merge(29, 32, 4, 4, "FATCA filing requirement",
                                  style_wrap)
            worksheet.write_merge(29, 32, 5, 5, "2nd TIN not.", style_wrap)
            worksheet.write_merge(29, 32, 6, 8,
                                  '13 Excess golden parachute \n     payments' + '\n\n' + '$' + str(
                                      income_dict.get(
                                          'excess_golden_perachute_payments',
                                          '')), style_wrap)
            worksheet.write_merge(29, 32, 9, 11,
                                  '14 Gross proceeds paid to an attorney' + '\n\n\n' + '$' + str(
                                      income_dict.get(
                                          'gross_proceeds_paid_to_an_attomey',
                                          '')), style_wrap)

            worksheet.write_merge(33, 36, 0, 2,
                                  '15a Section 409A deferrals' + '\n\n\n' + '$' + str(
                                      income_dict.get('section_409A_deferrals',
                                                      '')), style_wrap)
            worksheet.write_merge(33, 36, 3, 5,
                                  '15b Section 409A income' + '\n\n\n' + '$' + str(
                                      income_dict.get('section_409A_income',
                                                      '')), style_wrap)
            worksheet.write_merge(33, 36, 6, 8,
                                  '16 State tax withheld' + '\n\n\n' + '$' + str(
                                      income_dict.get('state_tax_withheld',
                                                      '')), style_wrap)
            worksheet.write_merge(33, 36, 9, 11,
                                  '17 State/Payer’s state no.' + '\n\n\n' + '$' + str(
                                      income_dict.get('state_payers_state_no',
                                                      '')), style_wrap)
            worksheet.write_merge(33, 36, 12, 14,
                                  '18 State income.' + '\n\n\n' + '$' + str(
                                      income_dict.get('state_income', '')),
                                  style_wrap)

            worksheet.write(37, 1, 'Form 1099-MISC', header_bold)
            worksheet.write(37, 3, 'Cat. No. 14425J', header_bold)
            worksheet.write(37, 6, 'www.irs.gov/Form1099MISC', header_bold)
            worksheet.write(37, 10,
                            'Department of the Treasury - Internal Revenue Service',
                            header_bold)
        fp = io.BytesIO()
        workbook.save(fp)

        report_id = self.env['wiz.report.1099.download'].create(
            {'report_file': base64.encodestring(fp.getvalue()),
             'report_file_name': filename})
        res = {
            'view_mode': 'form',
            'res_id': report_id.id,
            'res_model': 'wiz.report.1099.download',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
        return res
