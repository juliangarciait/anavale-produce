# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
import re

_logger = logging.getLogger(__name__)


class QuantProductRepackWizard(models.TransientModel):
    _name = 'quant.product.repack.wizard'
    _description = 'Repack Process by Product'

    product_id = fields.Many2one('product.product', string="Initial Product")
    location_id = fields.Many2one('stock.location', string="Location")
    lot_id = fields.Many2one('stock.production.lot', string="Lot")
    initial_qty = fields.Float(string="Initial Qty")
    main_qty = fields.Float(string="Main Lot Qty")
    product_dest_id = fields.Many2one('product.product', string="Destination Product")
    lot_dest_calculated = fields.Char(string='Destination Lot')
    lot_dest_id = fields.Many2one('stock.production.lot', string="Destination Lot")
    final_qty = fields.Float(string="Final Lot Qty")

    scrap_qty = fields.Float(string="Scrap Qty")

    @api.onchange('product_id', 'location_id')
    def _onchange_product_id(self):
        domain = [('lot_id', '!=', False), ('quantity', '>', 0)]
        if self.product_id:
            domain += [('product_id', '=', self.product_id.id)]
        if self.location_id:
            domain += [('location_id', '=', self.location_id.id)]
        lot_ids = [qt.lot_id.id for qt in self.env['stock.quant'].search(domain)]
        variant_ids = [pp.id for pp in self.product_id.product_variant_ids if pp != self.product_id]
        self.lot_id = False
        return {'domain': {'lot_id': [('id', 'in', lot_ids)],
                           'product_dest_id': [('id', 'in', variant_ids)]}}

    def _update_quantities(self, initial=0.0, main=0.0, final=0.0, scrap=0.0):
        self.initial_qty = initial
        self.main_qty = main
        self.final_qty = final
        self.scrap_qty = scrap

    def _update_lot_name(self):
        """
        Return Custom Name for Lot
        """
        if self.lot_dest_id:
            self.lot_dest_calculated = self.lot_dest_id.name
        else:
            initial_name = ''
            final_name = ''
            for value in self.product_id.product_template_attribute_value_ids:
                initial_name = value.product_attribute_value_id.name
                break
            for value in self.product_dest_id.product_template_attribute_value_ids:
                final_name = value.product_attribute_value_id.name
                break
            if not initial_name or not final_name:
                raise UserError(
                    _('it is not possible to calculate the batch name because the product has no variant name'))
            self.lot_dest_calculated = self.lot_id.name.replace(initial_name, final_name) + 'R'

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if self.lot_id and self.lot_dest_id:
            self._update_quantities(initial=self.lot_id.product_qty + self.lot_dest_id.product_qty,
                                    main=self.lot_id.product_qty,
                                    final=self.lot_dest_id.product_qty)
            self._update_lot_name()
            return
        # Search First Lots and Lots Product Repack
        elif self.lot_id.type_lot == 'product_repack':
            self._update_quantities()
            # Update Correct Parent and child
            if self.lot_id.parent_lod_id:
                # Change lots
                ref = self.lot_id.parent_lod_id
                ref_dest = self.lot_id
                self.lot_id = ref
                self.lot_dest_id = ref_dest
                # Change Product Dest
                self.product_dest_id = self.lot_dest_id.product_id
                return self._onchange_lot_id()
            if self.lot_id.child_lot_ids:
                lot_pp_child = [lot for lot in self.lot_id.child_lot_ids if lot.type_lot == 'product_repack']
                if lot_pp_child:
                    self.lot_dest_id = lot_pp_child[0]
                    # Change Product Dest
                    self.product_dest_id = self.lot_dest_id.product_id
                    return self._onchange_lot_id()
        # Calculate Lot Child
        self._update_quantities(initial=self.lot_id.product_qty, main=self.lot_id.product_qty)

    @api.onchange('product_dest_id')
    def _onchange_product_dest_id(self):
        if self.product_id and self.product_dest_id and self.lot_id:
            self._update_lot_name()

    @api.onchange('final_qty', 'scrap_qty')
    def _onchange_final_qty(self):
        self.main_qty = self.initial_qty - self.final_qty - self.scrap_qty
        self._check_valid_quantity()

    def _get_sum_qty(self):
        return self.main_qty + self.final_qty + self.scrap_qty

    def _check_valid_quantity(self):
        if self.main_qty < 0:
            raise UserError('Invalid Quantity, Please Fix it !')

    def _get_dest_lot_from_child_ids(self):
        if self.lot_id.child_lot_ids:
            for lot in self.lot_id.child_lot_ids:
                if '#1' or '#2' not in lot.name:
                    return lot
        return False

    def get_or_creat_lot(self, vals):
        sql = """select id, name 
                    from stock_production_lot 
                    where name=%(name)s AND product_id = %(product_id)s"""
        self.env.cr.execute(sql, vals)
        result = self.env.cr.dictfetchone()
        if result:
            return self.env['stock.production.lot'].sudo().browse(result.get('id'))
        return self.env['stock.production.lot'].sudo().create(vals)

    def get_name_lot_from_variant(self, product_id):
        name = ''
        for attr in product_id.product_template_attribute_value_ids:
            name += attr.product_attribute_value_id.name
        return name

    def process_repack(self):
        _logger.info("Product Repack!!!")
        # _logger.info(self._get_sum_qty_lines())
        if self._get_sum_qty() > self.initial_qty:
            raise UserError('Invalid quantities, Please Fix it !')
        if self.final_qty < 0.0:
            raise UserError('Final quantity in repack lots cannot be 0, Please Fix it !')
        # Create Inventory Adjust
        val = {
            'name': 'Product_repacker_Assistance v %s' % (str(self.id)),
            'product_ids': [(4, self.product_id.id)],
            'location_ids': [(4, self.location_id.id)],
        }
        si = self.env['stock.inventory'].sudo().create(val)
        si.sudo().action_start()
        # Create Lots
        if self.lot_dest_id:
            self.lot_dest_id.write({'analytic_tag_ids': self.lot_id.analytic_tag_ids})
        lot_ids = [self.lot_id, self.lot_dest_id or self.get_or_creat_lot({'name': self.lot_dest_calculated,
                                                                           'product_id': self.product_dest_id.id,
                                                                           'company_id': self.location_id.company_id.id,
                                                                           'parent_lod_id': self.lot_id.id,
                                                                           'analytic_tag_ids': self.lot_id.analytic_tag_ids,
                                                                           })]
        list_line_ids = [((0, 0, {
            'company_id': self.location_id.company_id.id,
            'prod_lot_id': lot_ids[0].id,
            'product_id': self.product_id.id,
            'location_id': self.location_id.id,
            'product_qty': self.main_qty
        })), ((0, 0, {
            'company_id': self.location_id.company_id.id,
            'prod_lot_id': lot_ids[1].id,
            'product_id': self.product_dest_id.id,
            'location_id': self.location_id.id,
            'product_qty': lot_ids[1].product_qty + self.final_qty #aumentar lo que originalmente tiene
        }))]
        si.line_ids = False
        si.line_ids = list_line_ids
        # Write Type Lot
        lot_ids[0].type_lot = 'product_repack'
        lot_ids[1].type_lot = 'product_repack'
        si.sudo().action_validate()
