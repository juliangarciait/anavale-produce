from odoo import api, fields, models, exceptions
from datetime import timedelta

class StockCrap(models.Model):
    _inherit = "stock.scrap"

    tag_ids = fields.Many2many("account.analytic.tag")
    lot_salida = fields.Many2one('stock.production.lot', 'Lote Producto',
        states={'done': [('readonly', True)]}, domain="[('product_id', '!=', product_id), ('company_id', '=', company_id)]")
    date_move = fields.Datetime('Move Date')

    def action_validate(self):
        if self.date_move:
            self.date = self.date_move
        if self.lot_id.product_qty < self.scrap_qty:
                raise exceptions.UserError('El lote no tiene suficientes cajas para la salida')
        else:
            res = super(StockCrap, self).action_validate()

    def do_scrap(self):
        self._check_company()
        for scrap in self:
            scrap.name = self.env['ir.sequence'].next_by_code('stock.scrap') or _('New')
            scrap_date = scrap._prepare_move_values()
            move = self.env['stock.move'].sudo().create(scrap_date)
            # master: replace context by cancel_backorder
            move.with_context(is_scrap=True)._action_done()
            if self.date_move:
                for m in move:
                    m.write({ 'date': self.date_move - timedelta(hours=6)})
                    for line in m.move_line_ids:
                        line.write({ 'date': self.date_move - timedelta(hours=6)})
                    for accmove in move.account_move_ids:
                        accmove.write({ 'date': self.date_move - timedelta(hours=6)})
            self.tag_ids = self.lot_salida.analytic_tag_ids
            if self.tag_ids:
                for line in move:
                    for acc_move in line.account_move_ids:
                        for invoice_line in acc_move.invoice_line_ids:
                            #if invoice_line.account_id.internal_group == 'expense':
                                #if not invoice_line.analytic_tag_ids:
                                invoice_line.analytic_tag_ids = self.lot_salida.analytic_tag_ids
            #actualizar valuacion de cajas
            if self.product_id.id == 561:
                precio_lote = 0
                lote = self.lot_id.id
                if self.lot_id.parent_lod_id.id:
                    lote = self.lot_id.parent_lod_id.id
                movimiento_recepcion = self.env['stock.move.line'].sudo().search([('location_id','=',4), ('lot_id','=',lote)])
                for mov in movimiento_recepcion:
                    if mov.move_id.purchase_line_id:
                        precio_lote = mov.move_id.purchase_line_id.price_unit
                if precio_lote > 0:
                    for line in move:
                        for acc_move in line.account_move_ids:
                            for invoice_line in acc_move.invoice_line_ids:
                                if invoice_line.balance < 0:
                                    invoice_line.with_context(check_move_validity=False).write({'credit':(abs(invoice_line.quantity) * precio_lote), 'balance':(invoice_line.quantity * precio_lote)})
                                if invoice_line.balance > 0:
                                    invoice_line.with_context(check_move_validity=False).write({'debit':(abs(invoice_line.quantity) * precio_lote), 'balance':(abs(invoice_line.quantity) * precio_lote)})
            scrap.write({'move_id': move.id, 'state': 'done'})
            if self.date_move:
                scrap.date_done = self.date_move
            else:
                scrap.date_done = fields.Datetime.now()
        return True
    
    