from odoo import api, fields, models

class StockCrap(models.Model):
    _inherit = "stock.scrap"

    tag_ids = fields.Many2many("account.analytic.tag")

    def action_validate(self):
        res = super(StockCrap, self).action_validate()

    def do_scrap(self):
        self._check_company()
        for scrap in self:
            scrap.name = self.env['ir.sequence'].next_by_code('stock.scrap') or _('New')
            move = self.env['stock.move'].create(scrap._prepare_move_values())
            # master: replace context by cancel_backorder
            move.with_context(is_scrap=True)._action_done()
            if self.tag_ids:
                for line in move:
                      for acc_move in line.account_move_ids:
                          for invoice_line in acc_move.invoice_line_ids:
                              if invoice_line.account_id.internal_group == 'expense':
                                  if not invoice_line.analytic_tag_ids:
                                    invoice_line.analytic_tag_ids = self.tag_ids
            scrap.write({'move_id': move.id, 'state': 'done'})
            scrap.date_done = fields.Datetime.now()
        return True