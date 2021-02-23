# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class QuantLotRepackWizard(models.TransientModel):
    _name = 'quant.lot.repack.wizard'
    _description = 'Repack Process by Lot'

    product_id = fields.Many2one('product.product', string="Product")
    location_id = fields.Many2one('stock.location', string="Location")
    lot_id = fields.Many2one('stock.production.lot', string="Lot")
    initial_qty = fields.Float(string="Initial Qty")
    final_qty = fields.Float(string="Main Lot Qty")
    lines_ids = fields.One2many('quant.lot.repack.lines.wizard',
                                'quant_lot_repack_id',
                                string="Repack Lines")

    scrap_qty = fields.Float(string="Scrap Qty")

    @api.onchange('product_id', 'location_id')
    def _onchange_product_id(self):
        domain = [('lot_id', '!=', False), ('quantity', '>', 0)]
        if self.product_id:
            domain += [('product_id', '=', self.product_id.id)]
        if self.location_id:
            domain += [('location_id', '=', self.location_id.id)]
        lot_ids = [qt.lot_id.id for qt in self.env['stock.quant'].search(domain)]
        self.lot_id = False
        return {'domain': {'lot_id': [('id', 'in', lot_ids)]}}

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if self.lot_id and not self.lot_id.child_lot_ids:
            self.scrap_qty = 0.0
            self.lines_ids = False
            if self.lot_id.parent_lod_id:
                ref = self.lot_id.parent_lod_id
                self.lot_id = ref
                self._onchange_lot_id()
            else:
                self.initial_qty = self.lot_id.product_qty
                self.final_qty = self.lot_id.product_qty
                split = ['1', '2']
                val = [(0, 0, {'lot_ref': self.lot_id.name + '#' + number, 'qty': 0.0})
                       for number in split]
                self.write(
                    {'lines_ids': val})
        elif self.lot_id and self.lot_id.child_lot_ids:
            self.scrap_qty = 0.0
            self.lines_ids = False
            # First Create Lines
            val = [(0, 0, {'lot_ref': lot.name, 'qty': lot.product_qty})
                   for lot in self.lot_id.child_lot_ids]
            self.write(
                {'lines_ids': val})
            self.initial_qty = self.lot_id.product_qty + self._get_sum_qty_lines()
            self.final_qty = self.lot_id.product_qty + self._get_sum_qty_lines()
        else:
            self.initial_qty = 0.0
            self.final_qty = 0.0
            self.scrap_qty = 0.0
            self.lines_ids = False

    @api.onchange('lines_ids', 'scrap_qty')
    def _onchange_lines_ids(self):
        self._check_valid_quantity()
        self.final_qty = self.initial_qty - self.scrap_qty
        self.final_qty -= self._get_sum_qty_lines()

    def _get_sum_qty_lines(self):
        return sum([line.qty for line in self.lines_ids])

    def _check_valid_quantity(self):
        if self._get_sum_qty_lines() + self.scrap_qty > self.initial_qty:
            raise UserError('Invalid Quantity, Please Fix it !')

    def get_or_creat_lot(self, vals):
        sql = """select id, name 
                    from stock_production_lot 
                    where name=%(name)s AND product_id = %(product_id)s"""
        self.env.cr.execute(sql, vals)
        result = self.env.cr.dictfetchone()
        if result:
            return result.get('id')
        return self.env['stock.production.lot'].sudo().create(vals).id

    def get_lot_child_quantity(self, lot_ref):
        for lot in self.lines_ids:
            if lot.lot_ref == lot_ref:
                return lot.qty
        return 0.0

    def _update_scrap_qty(self):
        StockScrap = self.env['stock.scrap']
        if self.scrap_qty > 0:
            # Create Scrap
            ss = StockScrap.sudo().create({
                'product_id': self.product_id.id,
                'scrap_qty': self.scrap_qty,
                'lot_id': self.lot_id.id,
                'location_id': self.location_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'origin': 'WZRPACK{}'.format(self.lot_id.id)
            })
            ss.sudo().action_validate()

    def process_repack(self):
        _logger.info("Repack!!!")
        # _logger.info(self._get_sum_qty_lines())
        for item in self.lines_ids:
            _logger.info(item.qty)
        if self._get_sum_qty_lines() <= 0:
            raise UserError('Quantity in repack lots cannot be 0, Please Fix it !')

        self._check_valid_quantity()
        # Scrap Qty
        self._update_scrap_qty()
        # Create Inventory Adjust
        vals = {
            'name': 'Repacker_Assistance v %s' % (str(self.id)),
            'product_ids': [(4, self.product_id.id)],
            'location_ids': [(4, self.location_id.id)],
        }
        si = self.env['stock.inventory'].sudo().create(vals)
        si.sudo().action_start()
        # Create Lots
        lot_childs = []
        for item in self.lines_ids:
            lot_childs.append(
                self.get_or_creat_lot({'name': item.lot_ref,
                                       'product_id': self.product_id.id,
                                       'company_id': self.location_id.company_id.id,
                                       'parent_lod_id': self.lot_id.id,
                                       'analytic_tag_ids': [(4, tag.id) for tag in self.lot_id.analytic_tag_ids],
                                       }))
        # ReOrganize and Create Move Lines
        lot_process = []
        for line in si.line_ids:
            if line.prod_lot_id.id == self.lot_id.id:
                line.product_qty = self.final_qty
            if (line.prod_lot_id.id in lot_childs
                    and line.prod_lot_id.id not in lot_process):
                lot_process.append(line.prod_lot_id.id)
                line.product_qty = self.get_lot_child_quantity(line.prod_lot_id.name)
        missing_lots = [lot_id for lot_id in lot_childs if lot_id not in lot_process]
        lot_ids = self.env['stock.production.lot'].browse(missing_lots)
        list_line_ids = []
        for lot_id in lot_ids:
            list_line_ids.append((0, 0, {
                'company_id': self.location_id.company_id.id,
                'prod_lot_id': lot_id.id,
                'product_id': self.product_id.id,
                'location_id': self.location_id.id,
                'product_qty': self.get_lot_child_quantity(lot_id.name)
            }))
        # Check Main Lot is in SI
        if self.final_qty > 0:
            ids = [line.prod_lot_id.id for line in si.line_ids]
            if self.lot_id.id not in ids:
                #Add main Lot qty
                list_line_ids.append((0, 0, {
                    'company_id': self.location_id.company_id.id,
                    'prod_lot_id': self.lot_id.id,
                    'product_id': self.product_id.id,
                    'location_id': self.location_id.id,
                    'product_qty': self.final_qty
                }))
        si.line_ids = list_line_ids
        si.sudo().action_validate()



class QuantLotRepackWizard(models.TransientModel):
    _name = 'quant.lot.repack.lines.wizard'
    _description = 'Repack Process by Lot'

    lot_ref = fields.Char(string="Lot")
    qty = fields.Float(string="Initial Qty")
    quant_lot_repack_id = fields.Many2one('quant.lot.repack.wizard', string="quant_lot_repack_id")
