from odoo import api, fields, models
from datetime import timedelta

class StockCrap(models.Model):
    _inherit = "stock.scrap"

    tag_ids = fields.Many2many("account.analytic.tag")
    date_move = fields.Datetime('Move Date')

    def action_validate(self):
        if self.date_move:
            self.date = self.date_move
        res = super(StockCrap, self).action_validate()

    def do_scrap(self):
        self._check_company()
        for scrap in self:
            scrap.name = self.env['ir.sequence'].next_by_code('stock.scrap') or _('New')
            scrap_date = scrap._prepare_move_values()
            move = self.env['stock.move'].create(scrap_date)
            # master: replace context by cancel_backorder
            move.with_context(is_scrap=True)._action_done()
            if self.date_move:
                for m in move:
                    m.write({ 'date': self.date_move - timedelta(hours=6)})
                    for line in m.move_line_ids:
                        line.write({ 'date': self.date_move - timedelta(hours=6)})
                    for accmove in move.account_move_ids:
                        accmove.write({ 'date': self.date_move - timedelta(hours=6)})
            if self.tag_ids:
                for line in move:
                      for acc_move in line.account_move_ids:
                          for invoice_line in acc_move.invoice_line_ids:
                              if invoice_line.account_id.internal_group == 'expense':
                                  if not invoice_line.analytic_tag_ids:
                                    invoice_line.analytic_tag_ids = self.tag_ids
            scrap.write({'move_id': move.id, 'state': 'done'})
            if self.date_move:
                scrap.date_done = self.date_move
            else:
                scrap.date_done = fields.Datetime.now()
        return True
    
    