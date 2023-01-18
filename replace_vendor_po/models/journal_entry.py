from odoo.http import request

def update_journal_entry(pickings, partner_id):
    for picking in pickings:
        journal_entries = request.env['account.move'].search([('ref', 'like', picking.name)])
        journal_entries.partner_id = partner_id