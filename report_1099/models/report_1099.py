# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd.
# Copyright (C) 2019 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models


class Report1099(models.Model):
    _name = 'report.1099'
    _description = 'Report 1099'

    income_list = [
        ('rent', '1. Rents'),
        ('royalty', '2. Royalties'),
        ('other', '3. Other Income'),
        ('federal_income_tax_withheld',
         '4. Federal income tax withheld'),
        ('fishing_boat_proceeds',
         '5. Fishing boat proceeds'),
        ('medical_and_health_care_payments',
         '6. Medical and health care payments'),
        ('non_emp_cmpr', '7. Nonemployee compensation'),
        ('sub_stitute_payments_in_lieu_of_dividends_or_interest',
         '8. Substitute payments in lieu of dividends or payments'),
        ('sale', '9. Direct Sales'),
        ('crop_insurance_proceeds', '10. Crop insurance proceeds'),
        ('11', '11. '), ('12', '12. '),
        ('excess_golden_perachute_payments',
         '13. Excess golden parachute payments'),
        ('gross_proceeds_paid_to_an_attomey',
         '14. Gross proceeds paid to an attorney'),
        ('section_409A_deferrals', '15a. Section 409A deferrals'),
        ('section_409A_income', '15.b. Section 409A income'),
        ('state_tax_withheld', '16. State tax withheld'),
        ("state_payers_state_no", "17. State/Payer's state no."),
        ('state_income', '18. State income')
    ]

    date = fields.Date()
    partner_id = fields.Many2one('res.partner', 'Vendor Name')
    id_number = fields.Char('TIN No.')
    bill_reference = fields.Char()
    type_income = fields.Selection(income_list, string="Income Type",
                                   default='non_emp_cmpr')
    amount = fields.Float()
    ssn_ein = fields.Selection([('ssn', 'SSN'),
                                ('ein', 'EIN')], string='SSN/EIN No.')
    legal_name = fields.Char()
    paid_date = fields.Date()
    paid_ref = fields.Char('Paid Reference')
    invoice_state = fields.Selection([('open', 'Open'), ('paid', 'Paid')],
                                     string='Invoice Status')
    check_number = fields.Integer()
    invoice_line_id = fields.Many2one('account.move.line',
                                      'Invoice Line Ref.', copy=False)
    currency_id = fields.Many2one("res.currency", 'Currency')

    def write(self, vals):
        res = super(Report1099, self).write(vals)
        for rec in self:
            if vals.get('type_income', False):
                if rec.invoice_line_id:
                    rec.invoice_line_id.type_income = vals['type_income']
        return res
