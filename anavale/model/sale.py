# -*- coding: utf-8 -*-
from xml.dom import ValidationErr
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare

import logging


_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    custom_state_delivery = fields.Char(string='State Delivery',
        compute='_compute_get_delivery_custom_state',
        help='Automatic assignation state from custom state delivery:\n',
        store=True,
        tracking=True)

    def update_amount_invoiced(self): 
        active_ids = self.env.context.get('active_ids', [])
        sales = self.search([('id', 'in', active_ids)])
        for sale in sales: 
            for line_sale in sale.order_line: 
                line_sale._get_to_invoice_qty()
                line_sale._get_invoice_qty()
                line_sale._compute_untaxed_amount_invoiced()
                line_sale._compute_untaxed_amount_to_invoice()

    def write(self, vals):
        if self.custom_state_delivery in ['Ready (No Delivered)', 'Done (Delivered)']:
            if vals['order_line']:
                if len(self.order_line) < len(vals['order_line']):
                    raise ValidationError("You can't add more lines in the current state ("+self.custom_state_delivery+")")
        return super(SaleOrder, self).write(vals)

    @api.depends('picking_ids.custom_state_delivery')
    def _compute_get_delivery_custom_state(self):
        for record in self:
            previus_status = record.custom_state_delivery
            pickings = self.mapped('picking_ids')
            if len(pickings)>0:
                sorte_list = pickings.sorted(key=lambda r: r.id)
                for picking in sorte_list:
                    if picking.state != 'cancel':
                        record.custom_state_delivery = dict(
                            picking._fields['custom_state_delivery'].selection).get(
                            picking.custom_state_delivery)
                        record.message_post(body='· Estado: {} --> {}'.format(previus_status, record.custom_state_delivery))
                        return
            record.custom_state_delivery = 'No status'

    def action_quotation_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        return super(SaleOrder, self.with_context(add_chatter_autofollow=False)).action_quotation_send()
        
    @api.model
    def action_quotation_sent(self):
        """ Metodo heredado to adds add_chatter_autofollow=False
            so res.partner is not added as follower to the chatter."""
        return super(SaleOrder, self.with_context(add_chatter_autofollow=False)).action_quotation_sent()

    def action_confirm(self):
        lines = self.order_line
        for line in lines:
            if line.analytic_tag_ids != line.lot_id.analytic_tag_ids: 
                line.analytic_tag_ids = line.lot_id.analytic_tag_ids.ids
            if not line.lot_id:
                raise UserError("Can't confirm without lot ")
        if not self.env.context.get('is_force'):
            self.check_still_quantity()
        date_order_default = self.date_order or fields.Datetime.now()
        res = super(SaleOrder, self).action_confirm()
        self.write({'date_order': date_order_default})
        return res

    def check_still_quantity(self):
        for line in self.order_line:
            line._onchange_lot_id(qty=line.product_uom_qty, sale_order_line=line.order_id.id)
            if line.product_id and line.lot_id and line.product_uom_qty > line.lot_available_sell:
                raise UserError('Maximum {} units for selected Lot {}! Please update before tried again'.format(
                    str(line.lot_available_sell), line.lot_id.name))

    @api.onchange('order_line')
    def onchange_order_line(self):
        list_mapped = []
        for line in self.order_line:
            if (line.product_id, line.lot_id) in list_mapped:
                raise UserError('Product {} with Lot {}! Already exist on the Order Lines. Please add amount in '
                                'existing line'.format(
                    str(line.product_id.name), line.lot_id.name))
            list_mapped.append((line.product_id, line.lot_id))


    #funcion para crear factura con la fecha del delivery
    def _create_invoices(self, grouped=False, final=False):
        res = super(SaleOrder, self)._create_invoices(grouped=False, final=False)
        invoice_date = 0
        for pick in self.picking_ids:
            if pick.state == 'done':
                invoice_date = pick.date_done
        if invoice_date != 0:
            res.invoice_date = invoice_date
            res.date = invoice_date

        #self._onchange_lot_id(self.product_uom_qty, self._origin.id)
        #if self.product_id and self.lot_id and self.product_uom_qty > self.lot_available_sell:
        #    raise UserError('Maximum %s units for selected Lot!' % self.lot_available_sell)

    # @api.model
    # def get_move_from_line(self, line):
        # move = self.env["stock.move"]
        # # i create this counter to check lot's univocity on move line
        # lot_count = 0
        # for m in line.order_id.picking_ids.mapped("move_lines"):
            # move_line_id = m.move_line_ids.filtered(lambda line: line.lot_id)
            # if move_line_id and line.lot_id == move_line_id[0].lot_id:
                # move = m
                # lot_count += 1
                # # if counter is 0 or > 1 means that something goes wrong
                # if lot_count != 1:
                    # raise UserError(_("Can't retrieve lot on stock"))
        # return move

    # @api.model
    # def _check_move_state(self, line):
        # if self.env.context.get("skip_check_lot_selection_move", False):
            # return True
        # if line.lot_id:
            # move = self.get_move_from_line(line)
            # if move.state == "confirmed":
                # move._action_assign()
                # move.refresh()
            # if move.state != "assigned":
                # raise UserError(
                    # _("Can't reserve products for lot %s") % line.lot_id.name
                # )
        # return True

    # def action_confirm(self):
        # res = super(SaleOrder, self.with_context(sol_lot_id=True)).action_confirm()
        # self._check_related_moves()
        # return res

    # def _check_related_moves(self):
        # if self.env.context.get("skip_check_lot_selection_qty", False):
            # return True
        # for line in self.order_line:
            # if line.lot_id:
                # unreserved_moves = line.move_ids.filtered(
                    # lambda move: move.product_uom_qty != move.reserved_availability
                # )
                # if unreserved_moves:
                    # raise UserError(
                        # _("Can not reserve products for lot %s") % line.lot_id.name
                    # )
            # self._check_move_state(line)
        # return True        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    tracking = fields.Selection(related='product_id.tracking', readonly=True)
    lot_id = fields.Many2one(comodel_name='stock.production.lot', string='Lot', copy=False)
    lot_available_sell = fields.Float('Stock', readonly=1)
    custom_state_delivery = fields.Char(related='order_id.custom_state_delivery')

    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        res['lot_id'] = self.lot_id.id
        return res

    @api.onchange('product_uom_qty')
    def onchange_quantity(self):
        self._onchange_lot_id(self.product_uom_qty, self._origin.id)
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
            res = self.sudo()._get_lots()
            lot_ids = res['lot_ids']  
            self.lot_id = False
            
        return {
            'domain': {'lot_id': [('id', 'in', lot_ids)],
                       'lot_available_sell': 0.0 }
        }    
        
    @api.onchange('lot_id')
    def _onchange_lot_id(self, qty=0.0, sale_order_line=False):
        quantity = 0.0
        if self.lot_id:
            res = self.sudo()._get_lots(self.lot_id.id,sale_order_line)
            quantity = res['quantity']
            self.product_uom_qty = qty

        self.lot_available_sell = quantity

    @api.onchange('lot_id', 'product_id')
    def _onchange_lot_sel_account(self):
        if self.lot_id and self.lot_id.analytic_tag_ids:
            self.analytic_tag_ids = False
            self.analytic_tag_ids = [(4, tag.id) for tag in self.lot_id.analytic_tag_ids]
     
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
            # ('qty_to_deliver', '>', 0),
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
        for quant in self.env['stock.quant'].search(domain + [('location_id', 'in', [8,25,26])]): #'child_of', self.order_id.warehouse_id.lot_stock_id.id)]):
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
            #avail[so.lot_id.id]['qty'] -= so.qty_to_deliver
         
        for lot in avail:
            if float_compare( avail[lot]['qty'], 0, precision_rounding=rounding) > 0:
               lot_ids.append(lot) 
               quantity += avail[lot]['qty']
        
        return {'lot_ids': lot_ids, 'quantity': quantity}
        
    # Originalmente este metodo se creo para compensar el hecho de que al crear manualmente
    # un stock.picking, aun viniendo de un sale.order, se pierde el campo stock.move.sale_line_id
    # por lo que el campo sale.order.line.qty_delivered no tomara en cuenta esos stock.moves, aun
    # cuando estos esten relacionados al sale.order y pertenezcan al mismo producto y lote.
    # TBD mantener liga stock.move.sale_line_id y stock.move.lot_id cuando el stock.picking
    # se crea manualmente viniendo de un sale.order
    def _compute_real_qty_to_deliver(self):
        qty = self.qty_to_deliver
        for move in self.move_ids.filtered(lambda q: q.state in ['done']):
            qty -= move.product_qty
        if qty < 0:
            qty = 0
        return qty

    def create(self, vals):
        # raise ValidationError('{}'.format(vals))
        so = vals[0]['order_id']
        so = self.env['sale.order'].browse(so)
        if so.state == 'sale':
            for line in vals:
                try:
                    if not line['lot_id']:
                        raise UserError("Can't create line without lot")
                except:
                    raise UserError("Can't create line without lot")
        res = super(SaleOrderLine, self).create(vals)