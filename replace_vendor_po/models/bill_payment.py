from odoo.http import request


def update_bill(bills, partner_id):
    for bill in bills:
        bill.partner_id = partner_id

        payments = request.env['account.payment'].search([('communication', '=', bill.name)])
        for payment in payments:
            print(payment.name)
            payment.partner_id = partner_id