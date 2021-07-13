from odoo import fields, models, api
from odoo import tools
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _update_stock_valuation_layer(self, move, product_id, price_unit):
        for layer in move.stock_valuation_layer_ids:
            if layer.product_id == product_id:
                layer.sudo().write({
                    'remaining_value': layer.remaining_qty * price_unit,
                    'value': layer.quantity * price_unit,
                    'unit_cost': price_unit
                })

    def payments_reconcile(self, move):
        pay_term_line_ids = move.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        domain = [('account_id', 'in', pay_term_line_ids.mapped('account_id').ids),
                  '|', ('move_id.state', '=', 'posted'), '&', ('move_id.state', '=', 'draft'),
                  ('journal_id.post_at', '=', 'bank_rec'),
                  ('partner_id', '=', move.commercial_partner_id.id),
                  ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                  ('amount_residual_currency', '!=', 0.0)]
        if move.is_inbound():
            domain.extend([('credit', '>', 0), ('debit', '=', 0)])
        else:
            domain.extend([('credit', '=', 0), ('debit', '>', 0)])
        lines = self.env['account.move.line'].search(domain)
        if len(lines) != 0:
            return lines

    def _update_work_flow_invoice(self, move):
        if move.state == 'posted':
            payment_state = move.invoice_payment_state
            move.button_draft()
            move.action_post()
            if payment_state in ('paid', 'in_payment'):
                # Refund Payment
                if move.invoice_has_outstanding:
                    lines = self.payments_reconcile(move)
                    for line in lines:
                        lines = self.env['account.move.line'].browse(line.id)
                        lines += move.line_ids.filtered(
                            lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.reconcile()

    @staticmethod
    def _get_list_lot_ids(lot_id):
        _logger.info(lot_id)
        result = [lot_id.id]
        for child_lot in lot_id.child_lot_ids:
            result.append(child_lot.id)
        return result

    def _update_account_move_from_sale(self, move_sale, product_id, price_unit):
        domain = [('lot_id', 'in', tuple(self._get_list_lot_ids(move_sale.lot_id))),
                  ('product_id', '=', move_sale.product_id.id)]
        lines = self.env['sale.order.line'].search(domain)
        for line in lines:
            # Update Purchase Move
            for move in line.move_ids:
                _logger.info("Move Update SALE")
                self._update_account_move(move, product_id, price_unit)
                self._update_stock_valuation_layer(move, product_id, price_unit)
            # Update Invoice Lines
            for ivl in line.invoice_lines:
                if ivl.move_id:
                    self._update_work_flow_invoice(ivl.move_id)

    def _update_account_move(self, stock_move, product_id, price_unit):
        for rec in self.env['account.move'].search([('stock_move_id', '=', stock_move.id)]):
            _logger.info("Move Update")
            _logger.info(rec.name)
            rec.button_draft()
            prepare_ids = []  # (1, ID, { values })
            for line_ac in rec.invoice_line_ids:
                if line_ac.product_id == product_id:
                    if line_ac.credit != 0:
                        prepare_ids.append((1, line_ac.id, {'credit': price_unit * abs(line_ac.quantity)}))
                    else:
                        prepare_ids.append((1, line_ac.id, {'debit': price_unit * abs(line_ac.quantity)}))
            if prepare_ids:
                rec.sudo().invoice_line_ids = prepare_ids
            rec.action_post()

    def action_update_valuation(self):
        _logger.info('update valuation')
        for record in self:
            for line in record.order_line:

                if line.product_id and line.price_total:
                    # Update Purchase Move
                    line._compute_total_invoiced()
                    for move in line.move_ids:
                        self._update_account_move(move, line.product_id, line.price_unit)
                        self._update_stock_valuation_layer(move, line.product_id, line.price_unit)
                        for move_sale in move.move_line_nosuggest_ids:
                            _logger.info(move_sale)
                            if move_sale.lot_id:
                                self._update_account_move_from_sale(move_sale, line.product_id, line.price_unit)



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    total_invoiced = fields.Float(compute='_compute_total_invoiced', string="Billed Total", store=True)

    #@api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _compute_total_invoiced(self):
        for line in self:
            total = 0.0
            for inv_line in line.invoice_lines:
                print("linea")
                print(inv_line.move_id.state)
                print(inv_line.move_id.type)
                print(inv_line.price_total)
                if inv_line.move_id.state not in ['cancel']:
                    if inv_line.move_id.type == 'in_invoice':
                        total += inv_line.price_total
                        print(total)
                    elif inv_line.move_id.type == 'in_refund':
                        total -= inv_line.price_total
            line.total_invoiced = total
            print(total)


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    total_invoiced = fields.Float('Total Billed', readonly=False, )

    def _select(self):
        return super(PurchaseReport, self)._select() + ", sum(l.total_invoiced) as total_invoiced"
