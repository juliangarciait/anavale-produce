from odoo import fields, models, api
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

    def _update_account_move_from_sale(self, move_sale, product_id, price_unit):
        domain = [('lot_id', '=', move_sale.lot_id.id), ('product_id', '=', move_sale.product_id.id)]
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
                    prepare_ids = []  # (1, ID, { values })
                    for ljournal in ivl.move_id.line_ids.filtered(lambda x: x.account_id.user_type_id.type in 'other'
                                                                            and x.account_id.user_type_id.internal_group in (
                                                                                    'expense', 'asset')):
                        _logger.info("update fe")
                        _logger.info(ljournal)
                        if ljournal.product_id == product_id:
                            if ljournal.credit != 0:
                                prepare_ids.append((1, ljournal.id, {'credit': price_unit * ljournal.quantity}))
                            else:
                                prepare_ids.append((1, ljournal.id, {'debit': price_unit * ljournal.quantity}))

                    if prepare_ids:
                        ivl.move_id.sudo().line_ids = prepare_ids

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
                    for move in line.move_ids:
                        self._update_account_move(move, line.product_id, line.price_unit)
                        self._update_stock_valuation_layer(move, line.product_id, line.price_unit)
                        for move_sale in move.move_line_nosuggest_ids:
                            _logger.info(move_sale)
                            if move_sale.lot_id:
                                self._update_account_move_from_sale(move_sale, line.product_id, line.price_unit)
