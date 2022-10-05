# -*- encoding: utf-8 -*-

from tokenize import String
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SettlementsSaleOrder(models.Model):
    _inherit = 'purchase.order'

    # llave foranea a liquidaciones

   # al darle click al boton abre el formulario

    def settlements_wizard_function(self):
        context = self._context.copy()
        fecha = self.date_order

        var = []
        for i in self.order_line:
            if i.product_id:
                var.append((0, 0,  {"date": fecha, "product_id": i.product_id.id,
                           "product_uom": i.product_uom.id, "price_unit": i.price_unit}))
                           
        logging.info('t'*500)
        logging.info(var)

        return {
            # 'res_model': 'sale.settlements',
            # #'res_id': self.partner_id.id,
            # 'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            # 'view_mode': 'form',
            # 'target': 'new',
            # 'name': 'Liquidaciones',
            # 'context': {'default_settlements_line_ids': var},
            # 'view_id': self.env.ref('liquidaciones.view_settlements').id

            'res_model': 'sale.settlements.wizard',
            # 'res_id': self.partner_id.id,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Liquidaciones',
            'context': {'default_settlements_line_ids': var},
            'view_id': self.env.ref('liquidaciones.selection_settlements_wizard_form').id
        }

    def settlements_button_function(self):
        context = self._context.copy()
        fecha = self.date_order

        var = []
        for i in self.order_line:
            if i.product_id:
                var.append((0, 0,  {"date": fecha, "product_id": i.product_id.id,
                           "product_uom": i.product_uom.id, "price_unit": i.price_unit}))

        return {
            # 'res_model': 'sale.settlements',
            # #'res_id': self.partner_id.id,
            # 'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            # 'view_mode': 'form',
            # 'target': 'new',
            # 'name': 'Liquidaciones',
            # 'context': {'default_settlements_line_ids': var},
            # 'view_id': self.env.ref('liquidaciones.view_settlements').id

            'res_model': 'sale.settlements.wizard',
            # 'res_id': self.partner_id.id,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Liquidaciones',
            'context': {'default_settlements_line_ids': var},
            'view_id': self.env.ref('liquidaciones.selection_settlements_wizard_form').id
        }

    def settlements_report_button_function(self):
        context = self._context.copy()
        fecha = self.date_order
        var = []
        for i in self.order_line:
            if i.product_id:
                var.append((0, 0,  {"date": fecha, "product_id": i.product_id.id,
                           "product_uom": i.product_uom.id, "price_unit": i.price_unit}))

        logging.info('t'*500)
        logging.info(var)

        return {
             'res_model': 'sale.settlements',
            # #'res_id': self.partner_id.id,
             'type': 'ir.actions.act_window',
            # 'view_type': 'form',
            # 'view_mode': 'form',
             'target': 'new',
             'name': 'Liquidaciones',
             'context': {'default_settlements_line_ids': var},
             'view_id': self.env.ref('liquidaciones.view_settlements').id

            #'res_model': 'sale.settlements.wizard',
            # 'res_id': self.partner_id.id,
            #'type': 'ir.actions.act_window',
            #'view_type': 'form',
            #'context': {'default_settlements_line_ids': var},
            #'view_id': self.env.ref('liquidaciones.selection_settlements_wizard_form').id
        }

class SettlementsInherit(models.Model):
    _name = 'sale.settlements'

    settlements_sale_order_ids = fields.One2many(
        'purchase.order', 'id', 'Lineas de Trabajo')
    settlements_line_ids = fields.One2many(
        'sale.settlements.lines', 'id', 'Lineas de Trabajo')


class SettlementsInheritLines(models.Model):
    _name = 'sale.settlements.lines'

    date = fields.Datetime(required=True, tracking=True, string="Fecha")
    product_id = fields.Many2one(
        'product.product', required=True, tracking=True, string="Producto")
    product_uom = fields.Many2one(
        'uom.uom', required=True, tracking=True, string="Medida")
    # Este lo escribe el usuario
    box_emb = fields.Integer(
        required=True, tracking=True, string="Cajas Embalaje")
    # Este lo escribe el usuario
    box_rec = fields.Integer(required=True, tracking=True, string="Cajas Rec.")
    price_unit = fields.Float(
        required=True, tracking=True, string="Precio Unitario")
    amount = fields.Float(required=True, tracking=True,
                          string="Importe", readonly=False,  compute='_compute_amount')
    # Costo del viaje, este lo escribe el usuario
    freight = fields.Float(required=True, tracking=True, string="Flete")
    purcharse_prise = fields.Float(
        required=True, tracking=True, string="Precio Compra")
    total = fields.Float(required=True,  string="Total")

    @api.onchange('price_unit', 'box_rec')
    def _compute_amount(self):
        for line in self:
            line.amount = line.price_unit*line.box_rec

    @api.onchange('purcharse_prise', 'box_rec')
    def _compute_total(self):
        for line in self:
            line.total = line.purcharse_prise*line.box_rec
