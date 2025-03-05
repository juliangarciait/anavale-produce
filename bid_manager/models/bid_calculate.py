# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import timedelta

class BidManagerLine(models.Model):
    _name = 'bid.manager.line'
    _description = 'Bid Manager Line'

    bid_manager_id = fields.Many2one('bid.manager', string='Bid ID', required=True, ondelete='cascade')
    bid_manager_price_type = fields.Selection([
        ('open', 'Abierto'),
        ('closed', 'Cerrado')
    ], related="bid_manager_id.price_type")
    product_variant_id = fields.Many2one('product.product', string='Producto', required=True)
    quantity = fields.Float(string='Cantidad', required=True)
    pallets = fields.Integer(string='Pallets', required=True)
    last_prices = fields.Float(string='Últimos Precios', compute='_compute_price')
    last_year_price = fields.Float(string='Precio Año Anterior', compute='_compute_price')
    price_unit = fields.Float(string='Precio Unitario', required=False)


    @api.depends('product_variant_id')
    def _compute_price(self):
        days = int(self.env['ir.config_parameter'].sudo().get_param('bid_manager.days_calculo_ultimos_dias', 60))
        for record in self:
            #calculo ultimos precios
            fecha_calculo = fields.Date.today() - timedelta(days=days)
            prices = self.env['purchase.order.line'].search([
                ('product_id', '=', record.product_variant_id.id),
                ('create_date', '>=', fecha_calculo)
            ]).mapped('price_unit')
            record.last_prices = sum(prices) / len(prices) if prices else 0.0

            #calculo anio pasado
            fecha_calculo_inicio_ly = fields.Date.today() - timedelta(days=days+365)
            fecha_calculo_final_ly = fields.Date.today() - timedelta(days=365)
            purchase_lines = self.env['purchase.order.line'].search([
                ('product_id', '=', record.product_variant_id.id),
                ('create_date', '>', fecha_calculo_inicio_ly),
                ('create_date', '<', fecha_calculo_final_ly)
            ])
            price_units = purchase_lines.mapped('price_unit')
            qty = purchase_lines.mapped('product_qty')
            # Calcular el precio promedio ponderado
            total_cost = sum(p * q for p, q in zip(price_units, qty))
            total_quantity = sum(qty)
            weighted_avg_price = total_cost / total_quantity if total_quantity else 0.0
            record.last_year_price = weighted_avg_price 


class BidManager(models.Model):
    _name = 'bid.manager'
    _description = 'Bid Manager'

    line_ids = fields.One2many('bid.manager.line', 'bid_manager_id', string='Líneas de Productos')
    pallets = fields.Integer(string='Pallets', compute='_compute_pallets')
    price_type = fields.Selection([
        ('open', 'Abierto'),
        ('closed', 'Cerrado')
    ], string='Tipo de Precio', required=True, default='open')
    commission = fields.Float(string='Comisión', required=False)
    freight_in = fields.Float(string='Freight In', compute='_compute_freight_in', store=True)
    freight_out = fields.Float(string='Freight Out', compute='_compute_freight_out', store=True)
    customs = fields.Float(string='Aduanas', required=False)
    boxes_cost = fields.Float(string='Cajas', compute='_calculate_boxes_cost', store=True)
    in_out = fields.Float(string='In/Out', compute='_compute_in_out', store=True)
    commission_buyer = fields.Float(string='Comisión Comprador', compute='_calc_commission_buyer', store=True)
    commission_seller = fields.Float(string='Comisión Vendedor', compute='_calc_commission_seller', store=True)
    others = fields.Float(string='Otros Costos', required=False)


    @api.depends('pallets')
    def _compute_freight_in(self):
        freight_cost = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.freight_in_cost', 10))
        for record in self:
            record.freight_in = freight_cost * record.pallets

    @api.depends('pallets')
    def _compute_freight_out(self):
        freight_cost = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.freight_out_cost', 10))
        for record in self:
            record.freight_out = freight_cost * record.pallets

    @api.depends('pallets')
    def _compute_in_out(self):
        in_out_cost = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.in_out_cost', 10))
        for record in self:
            record.in_out = in_out_cost * record.pallets


    @api.depends('line_ids.pallets')
    def _compute_pallets(self):
        for record in self:
            record.pallets = sum(record.line_ids.mapped('pallets'))

