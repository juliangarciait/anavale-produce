# -*- coding: utf-8 -*-
from odoo import models
from .pickings import update_pickings
from .journal_entry_line import update_journal_entry_line
from .journal_entry import update_journal_entry
from .bill_payment import update_bill


class PurchaseOrderRename(models.Model):

    _inherit = "purchase.order"

    def write(self, new_changes):
        purchase_order_id = self.id
        purchase_order_name = self.name

        if new_changes.get('partner_id'):
            partner_id = new_changes['partner_id']

            # update delivery order & pickings
            pickings = self.env['stock.picking'].search([('origin', '=', purchase_order_name)])
            if pickings != False:
                update_pickings(pickings, partner_id, purchase_order_name)
            else:
                pass

            # update journal entry line
            if pickings != False:
                update_journal_entry_line(pickings, partner_id)
            else:
                pass

            # update journal entry
            if pickings != False:
                update_journal_entry(pickings, partner_id)
            else:
                pass

            # Update Bill & Payment
            bills = self.env['account.move'].search([('invoice_origin', '=', purchase_order_name)])
            if bills != False:
                for bill in bills:
                    print(bill.name)
                update_bill(bills, partner_id)
            else:
                pass

        override_write = super(PurchaseOrderRename, self).write(new_changes)
        return override_write

        def updating_po(self, new_changes):
            self.write(new_changes)
