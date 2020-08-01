# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero
from itertools import groupby
import logging
_logger = logging.getLogger(__name__)

class Picking(models.Model):
    _inherit = "stock.picking"
    
    quality_ids = fields.One2many('stock.quality.check', 'picking_id', 'Checks')
    quality_count = fields.Integer(compute='_compute_quality_count')
    quality_check_todo = fields.Boolean('Pending checks', compute='_compute_quality_check_todo')
    create_lot_name = fields.Boolean('Create Lot Names', default=True)
    display_create_lot_name = fields.Boolean(compute='_compute_display_create_lot_name')
           
    @api.depends('state', 'picking_type_id', 
        'partner_id.sequence_id','partner_id.lot_code_prefix', 'location_dest_id')
    def _compute_display_create_lot_name(self):
        for picking in self:
            picking.display_create_lot_name = (
                # picking.partner_id.sequence_id and
                # picking.partner_id.lot_code_prefix and
                picking.picking_type_id.code == 'incoming' and 
                picking.state not in ('done', 'cancel') 
            )
             
    def _compute_quality_count(self):
        for picking in self:
            picking.quality_count = len(picking.quality_ids)
            
    def _compute_quality_check_todo(self):
        for record in self:
            #order = self.env['purchase.order'].search([('name', '=', record.origin)])
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', record.company_id.id)], limit=1)
            if warehouse and record.picking_type_id.code == 'internal' and record.location_dest_id == warehouse.lot_stock_id:
                record.quality_check_todo = True
            else:
                record.quality_check_todo = False
        
    def action_assign(self):
        """ Confirma que todos los stock.move.line
            correspondan con los lotes del stock.move,
            el cual a su vez es el mismo que el sale.order"""
        res = super(Picking, self).action_assign()
        moves = self.mapped('move_lines').filtered(lambda move: move.lot_id)
        if self.picking_type_id.code == 'outgoing' and moves:
            for ml in moves.mapped('move_line_ids'):
                if ml.product_id == ml.move_id.product_id and ml.lot_id != ml.move_id.lot_id:
                    raise UserError('Only same %s Lot allowed to deliver for product %s!' % (ml.move_id.lot_id.name, ml.product_id.name))        
        return res      
 
    def button_validate(self):
        """ Si es necesario crea lotes """
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
        no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
        # if no_reserved_quantities and no_quantities_done:
            # raise UserError(_('You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

        if self.display_create_lot_name and self.create_lot_name: # and not (no_reserved_quantities and no_quantities_done): # and (picking_type.use_create_lots or picking_type.use_existing_lots):
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )
            next_number = self.env['ir.sequence'].next_by_code('production.lot.%s.sequence' % self.partner_id.lot_code_prefix.lower())
            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        lot_name = self.get_next_lot_name(line.product_id, line.picking_id, next_number)
                        
                        lot = self.env['stock.production.lot'].create(
                            {'name': lot_name, 'product_id': line.product_id.id, 'company_id': line.move_id.company_id.id}
                        )
                        line.write({'lot_name': lot.name, 'lot_id': lot.id})

        #Check lot Traceability
        if self.picking_type_id.code == 'outgoing':
            try:
                self.sync_moves_with_sale_order()
            except Exception as e:
                raise UserError(_("Please check the following: %s" % str(e)))
        return super().button_validate()


    def search_inconsistencies(self):
        list_setted_moves = []
        is_inconsistency = False
        list_inconsistencies = []
        for line in self.move_line_ids:
            move_id = False
            for move in self.move_lines:
                if (line.lot_id == move.lot_id
                        and move.id not in list_setted_moves):
                    list_setted_moves.append(move.id)
                    move_id = move
                    break
            if not move_id:
                is_inconsistency = True
                list_inconsistencies.append(line)
        return list_inconsistencies


    def clear_delivery_lines(self):
        for move in self.move_line_ids:
            if move.product_uom_qty == 0:
                move.unlink()


    def update_empty_delivery_lines(self,list_ids_to_recreate):
        for move in self.move_line_ids:
            if (move.product_uom_qty != 0 and
                    move.lot_id.id in list(map(lambda x: x.get('lot_id'), list_ids_to_recreate))):
                        move.qty_done = move.product_uom_qty
                        # self.env.cr.execute(
                        #     """
                        #
                        #     UPDATE stock_move_line SET product_qty = '%s', qty_done = '%s' WHERE id = %s ;
                        #
                        #     """
                        #     % (move.product_uom_qty,move.product_uom_qty,move.id)
                        # )
                        # self.env.cr.commit()



    def force_do_unreserved_quants(self):
        for move in self.move_line_ids:
            if move.product_uom_qty > 0:
                # update reserverd stock quant
                result = self.env['stock.quant']._update_available_quantity(
                    move.product_id,
                    move.location_id,
                    move.product_uom_qty,
                    lot_id=move.lot_id)

                quants = self.env['stock.quant']._gather(move.product_id, move.location_id, lot_id=move.lot_id,strict=True)
                for quant in quants:
                    quant.write({"reserved_quantity": 0})
            self.env.cr.execute(
                """ 

                UPDATE stock_move_line SET product_uom_qty = 0, product_qty = 0 WHERE id = %s ;

                """
                % move.id
            )
            self.env.cr.commit()



    def get_default_tax_id(self,order_id_ref):
        #domain = [('company_id', '=', order_id_ref.company_id.id)]
        #default_company_tax = order_id_ref.env['account.tax'].sudo().search(domain, limit=1)
        tax_id_id = False
        #if default_company_tax:
        #    tax_id_id = default_company_tax.id
        for line in order_id_ref.order_line:
            if line.tax_id:
                tax_id_id = line.tax_id.id
                # order_id_ref.order_line.unlink()
                break
        return tax_id_id




    def sync_moves_with_sale_order(self):
        """
            From the moves_lines_ids
            The necessary stock moves are generated
            to separate by Lot
            @param: self : stock.picking ref

        """
        list_inconsistencies = self.search_inconsistencies()
        if len(list_inconsistencies)>0:
            #Inconsistency, FIX SO.
            order_id_ref = self.sale_id
            list_ids_to_recreate = self.get_list_new_quotation(list_inconsistencies)
            #Order fix
            order_id_ref.action_unlock()
            #Serching default Tax
            tax_id_id = self.get_default_tax_id(order_id_ref)
            #Set new orderlines
            order_id_ref.env['stock.picking'].create_sale_order_lines(order_id_ref, tax_id_id, list_ids_to_recreate)
            order_id_ref.action_done()
            self.clear_delivery_lines()
            self.update_empty_delivery_lines(list_ids_to_recreate)




    def custom_action_return_view_form(self, sale_id):
        domain = [('sale_id','=',sale_id.id),('state','=','confirmed')]
        sp = self.env['stock.picking'].sudo().search(domain)
        if sp:
            try:
                form_view_id = self.env.ref("stock.view_picking_form").id
            except Exception as e:
                form_view_id = False
            return {
                'type': 'ir.actions.act_window',
                'name': 'My Action Name',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'views': [(form_view_id, 'form')],
                'target': 'current',
            }

    def get_custom_product_price(self, sale_id, product_id):
        for line in sale_id.order_line:
            if line.product_id.id == product_id.id:
                return line.price_unit
        return False



    def get_list_new_quotation(self, list_inconsistencies):
        list = []
        for lines in list_inconsistencies:
            vals = {
                'product_id': lines.product_id.id,
                'name': lines.product_id.name,
                'order_id': self.sale_id.id,
                'lot_id': lines.lot_id.id,
                'product_uom': lines.product_id.uom_id.id,
                'product_uom_qty': lines.qty_done
            }
            price_unit = self.get_custom_product_price(self.sale_id,lines.product_id)
            if price_unit:
                vals['price_unit'] = price_unit

            list.append(vals)
        return list

    def create_sale_order_lines(self,sale_id,tax_id,list_ids):
        line_env = self.env['sale.order.line']
        for item in list_ids:
            vals = {
                'product_id': item.get('product_id'),
                'name': item.get('name'),
                'order_id': sale_id.id,
                'lot_id': item.get('lot_id'),
                'product_uom': item.get('product_uom'),
                'product_uom_qty': item.get('product_uom_qty'),
            }
            if tax_id:
                vals['tax_id']: [[6, False, [tax_id]]]
            if item.get('price_unit'):
                vals['price_unit'] = item.get('price_unit')
            line_env.sudo().create([vals])
        #update_sale_oder
        for line in sale_id.order_line:
            if line.lot_available_sell == 0 and line.product_uom_qty != 0:
                lot_id = line.lot_id
                qty = line.product_uom_qty
                price_unit = line.price_unit
                line.product_id_change()  # Calling an onchange method to update the
                line.lot_id = lot_id
                line._onchange_lot_id()
                line.product_uom_qty = qty
                line.price_unit = price_unit
                if not tax_id:
                    line.tax_id = False





    def create_sale_order_line_from_line_move(self, line_by_lot):
        """
            Create new sale.order.line associated
            to sale_id
            @param: self : stock.picking ref
            @param: line_by_lot : stock.move.line
        """
        line_env = self.env['sale.order.line']
        self.sale_id.sudo().write({'state': 'sale'})
        vals = {
            'product_id': line_by_lot.product_id.id,
            'name': line_by_lot.product_id.name,
            'order_id': self.sale_id.id,
            'lot_id' : line_by_lot.lot_id.id,
            'product_uom': line_by_lot.product_id.uom_id.id}
        new_line = line_env.create([vals])
        self.sale_id.sudo().write({'state': 'done'})
        # Calling an onchange method to update the record
        new_line.product_id_change()
        return new_line



    def create_stock_move_from_line_move(self, line_by_lot, sale_order_line):
        """
            Create new stock.move associated
            to stock.picking and sale.order.line
            @param: self : stock.picking ref
            @param: line_by_lot : stock.move.line
        """
        return self.env['stock.move'].create({
            'name': line_by_lot.product_id.name,
            'product_id': line_by_lot.product_id.id,
            'product_uom_qty': line_by_lot.qty_done,
            'product_uom': line_by_lot.product_uom_id.id,
            'picking_id': line_by_lot.picking_id.id,
            'location_id': line_by_lot.location.id.id,
            'location_dest_id': line_by_lot.location_dest_id.id,
            'sale_line_id': sale_order_line.id
        })



    
    def get_next_lot_name(self, product_id, picking_id, next_number):
        """ Method called by button "Create Lot Numbers", it automatically
            generates Lot names based on:
            - product.template.lot_code_prefix: 2 integers
            - res.partner.lot_code_prefix: 3 letters
            - Two digits Year
            - One dash "-"
            - res.partner.sequence.id: 4 integers sequence
            - product.product.variant: 2-3 chrs
            
            Samples: 02LMX20-0001#230
                     02FDP20-0016#230 """
        if not product_id.product_tmpl_id.lot_code_prefix:        
            raise UserError('Enter Product [%s] Lot Code and try again!.' % product_id.name)     
        if not picking_id.partner_id.lot_code_prefix:        
            raise UserError('Enter Vendor [%s] Lot Code and try again!.' % picking_id.partner_id.name)       
        if not picking_id.partner_id.sequence_id:        
            raise UserError('Assing a sequence to Vendor [%s] and try again!.' % picking_id.partner_id.name)             
        #next_number = self.env['ir.sequence'].next_by_code('production.lot.%s.sequence' % picking_id.partner_id.lot_code_prefix.lower())
        # se remueve anterior ya que aumenta contador cuando se piden varios articulos juntos
        if len(product_id.product_template_attribute_value_ids) == 0:
            return '%s%s%s' % (product_id.product_tmpl_id.lot_code_prefix,
                                 picking_id.partner_id.lot_code_prefix,
                                 next_number)
        else:
            try:   #revisa si la variante es numero y agrega simbolo antes del numero
                attribute = int(product_id.product_template_attribute_value_ids[0].product_attribute_value_id.name)
                attribute = '#%s' % (str(attribute))
            except ValueError:
                attribute = product_id.product_template_attribute_value_ids[0].product_attribute_value_id.name
            return '%s%s%s%s' % (product_id.product_tmpl_id.lot_code_prefix,
                                 picking_id.partner_id.lot_code_prefix,
                                 next_number,
                                 attribute)

                                 
class StockMove(models.Model):
    _inherit = 'stock.move'

    lot_id = fields.Many2one('stock.production.lot', string="Crate", copy=False)

    @api.model
    def create(self, vals):
        if vals.get('sale_line_id'):
            sale_line_id = self.env['sale.order.line'].browse(vals['sale_line_id'])
            if sale_line_id and sale_line_id.lot_id:
                vals.update({'lot_id': sale_line_id.lot_id.id})
        return super(StockMove, self).create(vals)

    # def write(self,vals):
        # res = super(StockMove, self).write(vals)
        # for rec in self:
            # if rec.sale_line_id and rec.picking_id and rec.lot_id and rec.move_line_ids and sum(rec.move_line_ids.mapped('qty_done')) == 0.0:
                # for line in rec.move_line_ids:
                    # line.lot_id = rec.lot_id.id
                    # line.qty_done = line.product_uom_qty #rec.product_uom_qty
        # return res

    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        if self.sale_line_id and self.sale_line_id.lot_id and self.product_id and self.product_id.tracking == 'lot':
            lot_id = self.sale_line_id.lot_id
                      
        return super()._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        if reserved_quant and self.sale_line_id:
            vals["lot_id"] = self.sale_line_id.lot_id.id
        return vals