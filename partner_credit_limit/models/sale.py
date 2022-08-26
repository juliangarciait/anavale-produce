# See LICENSE file for full copyright and licensing details.


from odoo import api, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def check_limit(self, delivery_count_before):
        self.ensure_one()
        partner = self.sudo().partner_id
        user_id = self.env['res.users'].sudo().search([
            ('partner_id', '=', partner.id)], limit=1)
        if user_id and not user_id.has_group('base.group_portal') or not \
                user_id:
            moveline_obj = self.env['account.move'].sudo()
            movelines = moveline_obj.search(
                [('partner_id', '=', partner.id),
                 ('state', '=', 'posted'),
                 ('type', '=', 'out_invoice')]
            )
            confirm_sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', self.id),
                                                                       ('invoice_status', '=', 'to invoice')])
            confirm_sale_order_delivery = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id),
                                                                                ('custom_state_delivery', '=','Waiting')])
            debit, credit = 0.0, 0.0
            due = 0
            amount_total = 0.0
            for status in confirm_sale_order:
                amount_total += status.amount_total
            for status in confirm_sale_order_delivery:
                amount_total += status.amount_total
            credit = partner.credit_insured + partner.credit_manual
            # credit = partner.credit_insured
            # if partner.credit_insured < partner.credit_manual:
            #     credit = partner.credit_manual
            for line in movelines:
                due += line.amount_residual_signed
            credit_used = credit - due - amount_total
            credit_available = credit_used + self.amount_total
            partner_overdue = partner.total_overdue
            if credit_used < 0 or partner_overdue > 0:
                if delivery_count_before == 0 :
                    if not partner.over_credit:
                        if partner.total_overdue > 0:
                            msg = '%s ' \
                                  ' have $%s in invoice overdue '% (self.partner_id.name, partner.total_overdue)
                        else:
                            msg = 'Your available credit' \
                                  ' is  $%s \nCheck "%s" Accounts or Credit ' \
                                  'Limits.' % (credit_available,
                                               self.partner_id.name)
                        raise UserError(_('You can not confirm Sale '
                                          'Order. \n' + msg))
                    else:
                        partner.over_credit = False
                # partner.write(
                #     {'credit_limit': credit - debit + self.amount_total})
            return True

    # def check_limit1(self):
    #     self.ensure_one()
    #     partner = self.partner_id
    #     user_id = self.env['res.users'].search([
    #         ('partner_id', '=', partner.id)], limit=1)
    #     if user_id and not user_id.has_group('base.group_portal') or not \
    #             user_id:
    #         moveline_obj = self.env['account.move.line']
    #         movelines = moveline_obj.search(
    #             [('partner_id', '=', partner.id),
    #              ('move_id.state', '=', 'posted'),
    #              ('account_id.user_type_id.name', 'in',
    #               ['Receivable', 'Payable'])]
    #         )
    #         confirm_sale_order = self.search([('partner_id', '=', partner.id),
    #                                           ('invoice_status', '=', 'to invoice')])
    #         #confirm_sale_order_delivery = self.search([('partner_id', '=', partner.id),
    #         #                                  ('custom_state_delivery', '=', 'Waiting')])
    #         debit, credit = 0.0, 0.0
    #         amount_total = 0.0
    #         for status in confirm_sale_order:
    #             amount_total += status.amount_total
    #         #for status in confirm_sale_order_delivery:
    #         #    amount_total += status.amount_total
    #         for line in movelines:
    #             credit += line.credit
    #             debit += line.debit
    #         partner_credit_limit = (partner.credit_limit - debit) + credit
    #         available_credit_limit = \
    #             (partner_credit_limit - debit)
    #         if (amount_total - debit) > available_credit_limit:
    #             if not partner.over_credit:
    #                 msg = 'Your available credit limit' \
    #                       ' Amount = %s \nCheck "%s" Accounts or Credit ' \
    #                       'Limits.' % (partner.credit_limit,
    #                                    self.partner_id.name)
    #                 raise UserError(_('You can not confirm Sale '
    #                                   'Order. \n' + msg))
    #             # partner.write(
    #             #     {'credit_limit': credit - debit + self.amount_total})
    #         return True

    def action_confirm(self):
        delivery_count_before = self.delivery_count
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.check_limit(delivery_count_before)
        return res

    #@api.constrains('amount_total')
    def check_amount(self):
        for order in self:
            order.check_limit()
