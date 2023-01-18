from odoo.http import request

def update_pickings(pickings, partner_id, purchase_order_name):
    for picking in pickings:
        picking.partner_id = partner_id

        # bills = request.env['account.move'].search([('invoice_origin', '=', purchase_order_name)])
        # if bills != False:
        #     for bill in bills:
        #         bill.partner_shipping_id = partner_id
