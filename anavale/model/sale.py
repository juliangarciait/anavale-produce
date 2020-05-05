# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

class SaleOrder(models.Model):
    _inherit = "sale.order"    

    def action_quotation_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        return super(SaleOrder, self.with_context(add_chatter_autofollow=False)).action_quotation_send()
        
    @api.model
    def action_quotation_sent(self):
        """ Metodo heredado to adds add_chatter_autofollow=False
            so res.partner is not added as follower to the chatter."""
        return super(SaleOrder, self.with_context(add_chatter_autofollow=False)).action_quotation_sent()
        
    # def action_confirm(self):
        # """ Method for 'Confirm' Button, adds add_chatter_autofollow=False
            # so res.partner is not added as follower to the chatter, also 
            # makes sure lot still available before confirming."""
        # res = super(SaleOrder, self.with_context(add_chatter_autofollow=False)).action_confirm()
        
        # for line in self.mapped('order_line').filtered(lambda line: line.lot_id):
            # # Get avail for this lot ommiting this sale.order.line
            # res = line._get_lots(line.lot_id.id, sale_order_line=line.id)
            # if line.product_uom_qty > res['quantity']:
                # raise UserError('Maximum %s units for selected Lot for Product %s!' % (res['quantity'], line.product_id.name))
        # return res        
  
    @api.model
    def get_move_from_line(self, line):
        move = self.env["stock.move"]
        # i create this counter to check lot's univocity on move lines
        lot_count = 0
        for m in line.order_id.picking_ids.mapped("move_lines"):
            move_line_id = m.move_line_ids.filtered(lambda line: line.lot_id)
            if move_line_id and line.lot_id == move_line_id[0].lot_id:
                move = m
                lot_count += 1
                # if counter is 0 or > 1 means that something goes wrong
                if lot_count != 1:
                    raise UserError(_("Can't retrieve lot on stock"))
        return move

    @api.model
    def _check_move_state(self, line):
        if self.env.context.get("skip_check_lot_selection_move", False):
            return True
        if line.lot_id:
            move = self.get_move_from_line(line)
            if move.state == "confirmed":
                move._action_assign()
                move.refresh()
            if move.state != "assigned":
                raise UserError(
                    _("Can't reserve products for lot %s") % line.lot_id.name
                )
        return True

    def action_confirm(self):
        res = super(SaleOrder, self.with_context(sol_lot_id=True)).action_confirm()
        self._check_related_moves()
        return res

    def _check_related_moves(self):
        if self.env.context.get("skip_check_lot_selection_qty", False):
            return True
        for line in self.order_line:
            if line.lot_id:
                unreserved_moves = line.move_ids.filtered(
                    lambda move: move.product_uom_qty != move.reserved_availability
                )
                if unreserved_moves:
                    raise UserError(
                        _("Can't reserve products for lot %s") % line.lot_id.name
                    )
            self._check_move_state(line)
        return True
        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    tracking = fields.Selection(related='product_id.tracking', readonly=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot', copy=False)
    lot_available_sell = fields.Float('Stock', readonly=1)

    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        res['lot_id'] = self.lot_id.id
        return res

    @api.onchange('product_uom_qty')
    def onchange_quantity(self):
        self._onchange_lot_id(self.product_uom_qty)
        if self.product_id and self.lot_id and self.product_uom_qty > self.lot_available_sell:
            raise UserError('Maximum %s units for selected Lot!' % self.lot_available_sell)
     
    @api.onchange('product_id')
    def product_id_change(self):
        super(SaleOrderLine, self).product_id_change()
        self.lot_id = False
        
    @api.onchange('product_id')
    def _onchange_product_id_set_lot_domain(self):
        lot_ids = []
        if self.order_id.warehouse_id and self.product_id:
            res = self._get_lots()
            lot_ids = res['lot_ids']  
            self.lot_id = False
            
        return {
            'domain': {'lot_id': [('id', 'in', lot_ids)],
                       'lot_available_sell': 0.0 }
        }    
        
    @api.onchange('lot_id')
    def _onchange_lot_id(self, qty=0.0):
        quantity = 0.0
        if self.lot_id:
            res = self._get_lots(self.lot_id.id)
            quantity = res['quantity']
            self.product_uom_qty = qty

        self.lot_available_sell = quantity
     
    def _get_lots(self, lot_id=False, sale_order_line=False):
        """ Compute lot availability including real in-stock,
            plus on-transit minus so already confirmed but
            not yet delivered.
            Params:
                lot_id: Integer stock.production.lot.id 
                   get lots only for this lot,
                   default False to get all lots
                sale_order_line: Integer sale.order.line.id
                  ommit this line when calculating avail """
        lot_ids = []        
        avail = {}
        quantity = 0.0        
        rounding = self.product_id.uom_id.rounding
        
        domain = [('product_id', '=', self.product_id.id), ('quantity', '>', 0)]
        so_domain = [('product_id', '=', self.product_id.id),
            ('qty_to_deliver', '>', 0),
            ('order_id.state', '=', 'sale')]
        if lot_id:
            domain += [('lot_id', '=', lot_id)]
            so_domain += [('lot_id', '=', lot_id)]
        else:
            domain += [('lot_id', '!=', False)]
            so_domain += [('lot_id', '!=', False)]
        if sale_order_line:
            so_domain += [('id', '!=', sale_order_line)]
            
        # Quants already in stock
        for quant in self.env['stock.quant'].search(domain + [('location_id', 'child_of', self.order_id.warehouse_id.lot_stock_id.id)]):
            avail.setdefault(quant.lot_id.id, {'lot': quant.lot_id.id, 'qty': 0.0})
            avail[quant.lot_id.id]['qty'] += quant.quantity 
        
        # Quant in transit
        for quant in self.env['stock.quant'].search(domain + [('location_id', 'child_of', self.order_id.warehouse_id.wh_input_stock_loc_id.id)]):
            avail.setdefault(quant.lot_id.id, {'lot': quant.lot_id.id, 'qty': 0.0})
            avail[quant.lot_id.id]['qty'] += quant.quantity 
            
        # Quants in sale.order with stock.picking not yet assigned nor done (this quants are not yet reserved)
        for so in self.env['sale.order.line'].search(so_domain):
            avail.setdefault(so.lot_id.id, {'lot': so.lot_id.id, 'qty': 0.0})
            avail[so.lot_id.id]['qty'] -= so._compute_real_qty_to_deliver()
         
        for lot in avail:
            if float_compare( avail[lot]['qty'], 0, precision_rounding=rounding) > 0:
               lot_ids.append(lot) 
               quantity += avail[lot]['qty']
        
        return {'lot_ids': lot_ids, 'quantity': quantity}
        
    def _compute_real_qty_to_deliver(self):
        qty = self.qty_to_deliver
        for move in self.move_ids.filtered(lambda q: q.state in ['cancel', 'draft']):
            qty -= move.product_qty
        if qty<0:
            qty=0
        return qty