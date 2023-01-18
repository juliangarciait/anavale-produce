from odoo.http import request

def update_journal_entry_line(pickings, partner_id):
    for picking in pickings:
        journal_entry_lines = request.env['account.move.line'].search([('ref', 'like', picking.name)])
        journal_entry_lines.partner_id = partner_id