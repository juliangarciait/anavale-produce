# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero

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
            order = self.env['purchase.order'].search([('name', '=', record.origin)])
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', record.company_id.id)], limit=1)
            if warehouse and order and record.picking_type_id.code == 'internal' and record.location_dest_id == warehouse.lot_stock_id:
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

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        lot_name = self.get_next_lot_name(line.product_id, line.picking_id)
                        
                        lot = self.env['stock.production.lot'].create(
                            {'name': lot_name, 'product_id': line.product_id.id, 'company_id': line.move_id.company_id.id}
                        )
                        line.write({'lot_name': lot.name, 'lot_id': lot.id})

        return super().button_validate()
    
    def get_next_lot_name(self, product_id, picking_id):
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
        next_number = self.env['ir.sequence'].next_by_code('production.lot.%s.sequence' % picking_id.partner_id.lot_code_prefix.lower())
        
        return '%s%s%s%s' % (product_id.product_tmpl_id.lot_code_prefix, 
                picking_id.partner_id.lot_code_prefix,
                next_number,
                product_id.product_template_attribute_value_ids[0].product_attribute_value_id.name)
                
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