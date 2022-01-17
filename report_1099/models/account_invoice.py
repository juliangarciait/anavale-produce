# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd.
# Copyright (C) 2019 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models, fields

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


class AccountMove(models.Model):
    _inherit = "account.move"

    is_1099 = fields.Boolean("Is 1099?")

    @api.depends('partner_id')
    def _compute_commercial_partner_id(self):
        """ Overridden method for Setting value of
            is_1099 from relevant partner """
        super(AccountMove, self)._compute_commercial_partner_id()
        repo_1099_obj = self.env['report.1099.config.partner']
        for move in self:
            is_1099 = False
            if move.type in ('in_invoice', 'in_refund'):
                rep_1099_conf_rec = repo_1099_obj.sudo().search(
                                    [('partner_id', '=', move.partner_id.id)],
                                    limit=1)
                is_1099 = rep_1099_conf_rec.is_1099
            move.is_1099 = is_1099

    @api.model
    def default_get(self, default_fields):
        """ Setting default value of is_1099 from relevant partner """
        res = super(AccountMove, self).default_get(default_fields)
        partner_ids = self._context.get('partner_tags_ids', False)
        partner = self.env['res.partner'].browse(partner_ids)
        repo_1099_obj = self.env['report.1099.config.partner']
        if partner:
            rep_1099_conf_rec = repo_1099_obj.sudo().search([
                                              ('partner_id', '=', partner.id)
                                              ], limit=1)
            res['is_1099'] = rep_1099_conf_rec and \
                rep_1099_conf_rec.is_1099 or False
        return res

    @api.onchange('partner_id')
    def onchange_partner_inv(self):
        repo_1099_obj = self.env['report.1099.config.partner']
        for rec in self:
            if rec.partner_id:
                rep_1099_conf_rec = repo_1099_obj.sudo().search([
                                      ('partner_id', '=', rec.partner_id.id)
                                      ], limit=1)
                for line in rec.invoice_line_ids:
                    line.is_1099 = rep_1099_conf_rec.is_1099
                    if rep_1099_conf_rec.is_1099:
                        line.type_income = rep_1099_conf_rec.type_income
                    else:
                        line.type_income = False


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_1099 = fields.Boolean()
    type_income = fields.Selection(income_list, string="Income Type")

    @api.model
    def default_get(self, default_fields):
        """ Setting default value of is_1099 from relevant partner """
        res = super(AccountMoveLine, self).default_get(default_fields)
        partner_ids = self._context.get('partner_tags_ids', False)
        partner = self.env['res.partner'].browse(partner_ids)
        if partner:
            repo_1099_obj = self.env['report.1099.config.partner']
            rep_1099_conf_rec = repo_1099_obj.sudo().search(
                                         [('partner_id', '=', partner.id)],
                                         limit=1)
            res['is_1099'] = rep_1099_conf_rec and \
                rep_1099_conf_rec.is_1099 or False
            if rep_1099_conf_rec and rep_1099_conf_rec.is_1099:
                res['type_income'] = rep_1099_conf_rec.type_income
        return res

    @api.onchange('is_1099')
    def onchange_is_1099(self):
        repo_1099_obj = self.env['report.1099.config.partner']
        for rec in self:
            if rec.partner_id:
                rep_1099_conf_rec = repo_1099_obj.sudo().search(
                                        [('partner_id', '=', rec.partner_id.id)
                                         ], limit=1)
                if rep_1099_conf_rec.is_1099 and rec.is_1099:
                    rec.type_income = rep_1099_conf_rec.type_income
                else:
                    rec.type_income = False
            else:
                rec.type_income = False

    @api.onchange('partner_id')
    def onchange_partner_1099(self):
        if self.partner_id:
            rep_1099_conf_rec = \
                self.env['report.1099.config.partner'].sudo().search(
                                      [('partner_id', '=', self.partner_id.id)
                                       ], limit=1)
            self.is_1099 = rep_1099_conf_rec and rep_1099_conf_rec.is_1099
            if self.partner_id and rep_1099_conf_rec \
                    and rep_1099_conf_rec.is_1099:
                self.type_income = rep_1099_conf_rec.type_income
            else:
                self.type_income = False


class AccountPayment(models.Model):
    _inherit = "account.payment"

    is_1099 = fields.Boolean()
