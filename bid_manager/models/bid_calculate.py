# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
import json
import ast

class BidManagerLine(models.Model):
    _name = 'bid.manager.line'
    _description = 'Bid Manager Line'

    bid_manager_id = fields.Many2one('bid.manager', string='Bid ID')
    # bid_manager_price_type = fields.Selection([
    #     ('open', 'Abierto'),
    #     ('closed', 'Cerrado')
    # ], related="bid_manager_id.price_type")
    bid_manager_price_type =  fields.Selection(related='bid_manager_id.price_type', readonly=True)
    product_variant_id = fields.Many2one('product.product', string='Producto', required=True)
    quantity = fields.Float(string='Cantidad', required=True)
    pallets = fields.Integer(string='Pallets', required=True)
    last_prices = fields.Float(string='Últimas Ventas', compute='_compute_price')
    last_year_price = fields.Float(string='Venta Año Anterior', compute='_compute_price')
    price_unit = fields.Float(string='Costo Unitario', required=False)
    price_sale_estimate = fields.Float(string='Precio Venta estimado', required=False)


    # @api.model
    # def write(self, vals):
    #     res = super(BidManagerLine, self).write(vals)
    #     if 'pallets' in vals and self.bid_manager_id:
    #         self.bid_manager_id._compute_lines_ids()
    #     return res

    
    @api.model
    def create(self, vals):
        res = super(BidManagerLine, self).create(vals)
        if 'pallets' in vals and self.bid_manager_id:
            self.bid_manager_id._compute_lines_ids()
        return res


    @api.depends('product_variant_id')
    def _compute_price(self):
        days = int(self.env['ir.config_parameter'].sudo().get_param('bid_manager.days_calculo_ultimos_dias', 60))
        for record in self:
            #calculo ultimos precios
            fecha_calculo = fields.Date.today() - timedelta(days=days)
            prices = self.env['sale.order.line'].search([
                ('product_id', '=', record.product_variant_id.id),
                ('create_date', '>=', fecha_calculo)
            ]).mapped('price_unit')
            record.last_prices = sum(prices) / len(prices) if prices else 0.0

            #calculo anio pasado
            fecha_calculo_inicio_ly = fields.Date.today() - timedelta(days=days+365)
            fecha_calculo_final_ly = fields.Date.today() - timedelta(days=365)
            sales_lines = self.env['sale.order.line'].search([
                ('product_id', '=', record.product_variant_id.id),
                ('create_date', '>', fecha_calculo_inicio_ly),
                ('create_date', '<', fecha_calculo_final_ly)
            ])
            price_units = sales_lines.mapped('price_unit')
            qty = sales_lines.mapped('product_uom_qty')
            # Calcular el precio promedio ponderado
            total_cost = sum(p * q for p, q in zip(price_units, qty))
            total_quantity = sum(qty)
            weighted_avg_price = total_cost / total_quantity if total_quantity else 0.0
            record.last_year_price = weighted_avg_price 


class BidManager(models.Model):
    _name = 'bid.manager'
    _description = 'Bid Manager'

    line_ids = fields.One2many('bid.manager.line', 'bid_manager_id', string='Líneas de Productos')
    partner_id = fields.Many2one('res.partner', string='Proveedor')
    partner_new =  fields.Boolean(string='Nuevo Proveedor')
    partner_is_mx =  fields.Boolean(string='Proveedor es Mexicano')
    partner_new_name = fields.Char(string='Nombre del Proveedor')
    price_type = fields.Selection([
        ('open', 'Abierto'),
        ('closed', 'Cerrado')
    ], string='Tipo de Precio', default='open')
    commission = fields.Float(string='Comisión %', default=8)
    
    # Nuevo campo computado para el producto principal
    main_product_id = fields.Many2one('product.template', string='Producto Principal', compute='_compute_main_product', store=True)
    
    freight_in_check = fields.Boolean(string='Manual?')
    freight_in = fields.Float(string='Freight In', compute="_compute_calc_based_partner", store=True)
    
    freight_out_check = fields.Boolean(string='Manual?', store=True)
    freight_out = fields.Float(string='Freight Out', compute="_compute_freight_out", store=True)

    custom_check = fields.Boolean(string='Manual?', store=True)
    customs = fields.Float(string='Aduanas', compute='_compute_calc_based_partner', store=True)

    boxes_check = fields.Boolean(string='Manual?', store=True, default=True)
    boxes_cost = fields.Float(string='Cajas', compute='_compute_calc_based_partner', store=True)

    in_out_check = fields.Boolean(string='Manual?', store=True)
    in_out = fields.Float(string='In/Out', compute='_compute_calc_based_partner', store=True)

    commission_buyer = fields.Float(string='Comisión Comprador', compute='_calc_commission_buyer', store=True)
    commission_anavale = fields.Float(string='Comisión Anavale', compute='_calc_commission_buyer', store=True)
    commission_saler = fields.Float(string='Comisión Vendedor', compute='_calc_commission_saler',store=True)
    others = fields.Float(string='Otros Costos', required=False)

    lines_amount_calc = fields.Float(string='costo producto', compute='_compute_lines_ids', required=False)
    quantity = fields.Integer(string='Cantidad', compute='_compute_lines_ids')
    pallets = fields.Integer(string='Pallets', compute='_compute_lines_ids')

    hidden_cost = fields.Float(string='Costos ocultos', compute='_calc_hidden_cost', required=False)
    freight_in_calculate = fields.Float(string='Freight In', compute="_compute_freight_in", store=True)

    gross_profit = fields.Float(string='Ganacia bruta', compute='_calc_gross_profit', store=True)
    net_profit = fields.Float(string='Ganacia neta', compute='_calc_gross_profit', store=True)
    price_unit_calc = fields.Float(string='Costo unitario calculado', compute='_calc_gross_profit', store=True)
    profit_percentage = fields.Float(string='Porcentaje de Ganancia', compute='_calc_commission_buyer', store=True)
    profit_anavale = fields.Float(string='Ganancia Anavale', compute='_calc_commission_buyer', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to approve', 'To Approve'),
        ('approved', 'Approved'),
        ('done', 'Compra'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    purchase_order = fields.Many2one('purchase.order', string='Purchase')

    @api.onchange('partner_new')
    def _partner_new(self):
        for record in self:
            if record.partner_new:
                record.partner_id = None
                record.partner_is_mx = True

    @api.onchange('boxes_check')
    def _boxes_check_change(self):
        for record in self:
            if record.boxes_check == False:
                record.boxes_cost = 0

    @api.depends('line_ids.pallets', 'line_ids.quantity', 'line_ids.price_unit', 'line_ids.price_sale_estimate', 'price_type')
    def _compute_lines_ids(self):
            for record in self:
                record.pallets = sum(record.line_ids.mapped('pallets'))
                record.quantity = sum(record.line_ids.mapped('quantity'))
                calc = 0
                for line in record.line_ids:
                    calc += line.quantity * line.price_sale_estimate
                record.lines_amount_calc = calc
                

    @api.depends('pallets', 'quantity', 'lines_amount_calc', 'partner_id', 'partner_is_mx', 'freight_in_check', 'freight_out_check', 'in_out_check', 'boxes_check')
    def _compute_calc_based_partner(self):
        mexico_id = self.env['res.country'].search([('code', '=', 'MX')],limit=1).id
        aduana = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.aduana', 600))
        freight_out = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.freight_out', 220))
        boxes_prom = 1.8
        in_out_cost = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.in_out_cost', 1.9))
        for record in self:
            #no es partner nuevo y ya seleccionamos partner
            if record.partner_id and record.partner_new == False:
                if record.freight_in_check == False:
                    partner_tag_text = record.partner_id.lot_code_prefix
                    partner_tag = self.env['account.analytic.tag'].sudo().search([('name', '=', partner_tag_text)]).ids
                    freight_cost_calc = self.env['account.move.line'].sudo().search([('analytic_tag_ids','in',partner_tag ),('account_id', '=', 1387)], order="id desc", limit=5)
                    freight_in = 0
                    if len(freight_cost_calc)>0:
                        for freight in freight_cost_calc:
                            freight_in += freight.balance
                        freight_in = freight_in / len(freight_cost_calc)
                        record.freight_in = freight_in
                if record.freight_out_check == False:
                        record.freight_out = freight_out
                if record.custom_check == False:
                    if record.partner_id.country_id.id == mexico_id:
                        record.customs = aduana
                    else:
                        record.customs = 0
                if record.boxes_check == False:
                    record.boxes_cost == record.quantity * boxes_prom
                if record.in_out_check == False:
                    record.in_out = in_out_cost * record.pallets
            #es partner nuevo y es mexicano
            elif record.partner_new and record.partner_is_mx:
                if record.freight_in_check == False:
                    # partner_tag_text = record.partner_id.lot_code_prefix
                    # partner_tag = self.env['account.analytic.tag'].sudo().search([('name', '=', partner_tag_text)]).ids
                    freight_cost_calc = self.env['account.move.line'].sudo().search([('account_id', '=', 1387),('balance','>',500)], order="id desc", limit=10)
                    freight_in = 0
                    if len(freight_cost_calc)>0:
                        for freight in freight_cost_calc:
                            freight_in += freight.balance
                        freight_in = freight_in / len(freight_cost_calc)
                        record.freight_in = freight_in
                if record.freight_out_check == False:
                        record.freight_out = freight_out
                if record.custom_check == False:   
                    record.customs = aduana
                if record.boxes_check == False:
                    record.boxes_cost == record.quantity * boxes_prom
                if record.in_out_check == False:
                    record.in_out = in_out_cost * record.pallets   
            #partner nuevo y no es mexicano         
            elif record.partner_new and record.partner_is_mx == False:
                if record.freight_in_check == False:
                    record.freight_in = 0
                if record.freight_out_check == False:
                        record.freight_out = freight_out
                if record.custom_check == False:   
                    record.customs = 0
                if record.boxes_check == False:
                    record.boxes_cost == 0
                if record.in_out_check == False:
                    record.in_out = in_out_cost * record.pallets


    @api.depends('lines_amount_calc')
    def _calc_commission_saler(self):            
        commision_saler_percentage = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.commission_saler_percent', .5)) / 100
        for record in self:
            venta_calculada = record.lines_amount_calc * commision_saler_percentage
            record.commission_saler = venta_calculada

    
    @api.depends('lines_amount_calc','freight_in', 'freight_out', 'boxes_cost', 'customs', 'in_out', 'others', 'hidden_cost', 'price_type', 'commission')
    def _calc_gross_profit(self):
        for record in self:
            if record.price_type == 'open':
                record.gross_profit = record.lines_amount_calc - record.freight_in - record.freight_out 
                record.gross_profit = record.gross_profit - record.boxes_cost - record.customs - record.in_out
                record.gross_profit = record.gross_profit - record.others - record.hidden_cost 
            else:
                cost = float(sum(line.price_unit * line.quantity for line in record.line_ids))
                record.gross_profit = record.lines_amount_calc - record.freight_in - record.freight_out 
                record.gross_profit = record.gross_profit - record.boxes_cost - record.customs - record.in_out
                record.gross_profit = record.gross_profit - record.others - record.hidden_cost - cost 

    @api.depends('gross_profit')
    def _calc_commission_buyer(self):
            commision_buyer_percentage = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.commission_buyer_percent', 15)) / 100
            
            admin_fee_percentage = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.admin_fee_percentage', 5)) / 100
            for record in self:
                commision_anavale_percentage = record.commission / 100
                if record.price_type == 'open':
                    commision_anavale_percentage = record.commission / 100
                    record.commission_buyer = record.gross_profit * commision_buyer_percentage
                    record.commission_anavale = record.gross_profit * commision_anavale_percentage
                    admin_fee = record.gross_profit * admin_fee_percentage
                    record.net_profit = record.gross_profit - record.commission_buyer - record.commission_anavale - admin_fee - record.commission_saler
                    record.profit_anavale = record.commission_anavale
                    if record.net_profit > 0 and record.quantity > 0:
                        record.price_unit_calc = record.net_profit / record.quantity
                        record.profit_percentage = record.commission
                    else: record.price_unit_calc = 0
                else:
                    record.commission_buyer = record.gross_profit * commision_buyer_percentage
                    admin_fee = record.gross_profit * admin_fee_percentage
                    record.net_profit = record.gross_profit - record.commission_buyer - admin_fee - record.commission_saler
                    if record.lines_amount_calc > 0:
                        record.profit_percentage = record.net_profit / record.lines_amount_calc
                        record.profit_anavale = record.net_profit
                    else : record.profit_percentage = 0
                    #porcentaje de ganancia


    @api.depends('partner_id', 'lines_amount_calc')
    def _calc_hidden_cost(self):
        # percentage_hidden_cost = 0
        # hidden_cost = self.env['ir.config_parameter'].sudo().get_param('bid_manager.additional_expense_ids', '[]')
        # hidden_cost = ast.literal_eval(hidden_cost)
        # hidden_cost = self.env['additional.expense'].sudo().search([('id', 'in', hidden_cost)])
        # for hd in hidden_cost:
        #     percentage_hidden_cost += hd.percentage
        # for record in self:
        #     record.hidden_cost = self.lines_amount_calc * (percentage_hidden_cost/100)
        for record in self:
            record.hidden_cost = 0


    def action_submit_for_approval(self):
        for record in self:
            record.state = 'to approve'


    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_approve(self):
        for record in self:
            record.state = 'approved'

    def action_create_purchase(self):
        PurchaseOrder = self.env['purchase.order']
        PurchaseOrderLine = self.env['purchase.order.line']
        if self.partner_new:
            chk_partner = self.env['res.partner'].search([('name','=',self.partner_new_name)])
            if chk_partner:
                raise ValidationError("el partner que esta tratando de crear ya existe")
            else:
                current_uid = self._context.get('uid')
                user = self.env['res.users'].browse(current_uid)
                partner_new_created = self.env['res.partner'].create({
                    'name': self.partner_new_name,
                    'purchaseperson_id' : user.id
                })
                self.partner_id = partner_new_created
        # Crear la orden de compra
        purchase_order = PurchaseOrder.create({
            'partner_id': self.partner_id.id,
            'origin': f'Bid #{self.id}',
            'importacion' : 'Si',
            'user_id' : user.id
        })

        # Crear las líneas de orden de compra
        for line in self.line_ids:
            PurchaseOrderLine.create({
                'order_id': purchase_order.id,
                'product_id': line.product_variant_id.id,
                'name': line.product_variant_id.name,
                'product_qty': line.quantity,
                'pallets' : line.pallets,
                'product_uom': line.product_variant_id.uom_id.id,
                'price_unit': 1.0 if self.price_type == 'open' else line.price_unit,
                'date_planned': fields.Date.today(),
            })

        # Asociar la orden a la licitación
        self.purchase_order = purchase_order.id
        self.state = 'done'
        return {
                'type': 'ir.actions.act_window',
                'name': 'Orden de Compra',
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': purchase_order.id,
                'target': 'current',
                }

    @api.model
    def name_get(self):
        result = []
        for record in self:
            name = f"Cotizacion #{record.id}"
            if record.partner_id:
                name += f" - [{record.partner_id.name}]"
            result.append((record.id, name))
        return result


    def write(self, vals): 
        res = super(BidManager, self).write(vals)
        if self.price_type == 'open':
            for line in self.line_ids:
                line.price_unit = self.price_unit_calc


    @api.depends('line_ids', 'line_ids.product_variant_id', 'line_ids.quantity')
    def _compute_main_product(self):
        """Calcula el producto con mayor cantidad entre las líneas"""
        for record in self:
            max_qty = 0
            main_product = False
            products_dict = {}
            
            for line in record.line_ids:
                # Agrupamos por template_id y sumamos cantidades
                template_id = line.product_variant_id.product_tmpl_id.id
                if template_id in products_dict:
                    products_dict[template_id]['qty'] += line.quantity
                else:
                    products_dict[template_id] = {
                        'qty': line.quantity,
                        'template_id': template_id
                    }
            
            # Buscamos el template con mayor cantidad
            for template, data in products_dict.items():
                if data['qty'] > max_qty:
                    max_qty = data['qty']
                    main_product = data['template_id']
            
            record.main_product_id = main_product










    







    # @api.depends('line_ids.pallets')
    # def _compute_pallets(self):
    #     for record in self:
    #         record.pallets = sum(record.line_ids.mapped('pallets'))

    # @api.depends('line_ids.quantity')
    # def _compute_quantity(self):
    #     for record in self:
    #         record.quantity = sum(record.line_ids.mapped('quantity'))


"""     @api.depends('partner_id')
    def _compute_freight_in(self):
        for record in self:
            if record.partner_id:
                partner_tag_text = record.partner_id.lot_code_prefix
                partner_tag = self.env['account.analytic.tag'].sudo().search([('name', '=', partner_tag_text)]).ids
                freight_cost_calc = self.env['account.move.line'].sudo().search([('analytic_tag_ids','in',partner_tag ),('account_id', '=', 1387)], order="id desc", limit=5)
                freight_in = 0
                if len(freight_cost_calc)>0:
                    for freight in freight_cost_calc:
                        freight_in += freight.balance
                    freight_in = freight_in / len(freight_cost_calc)
                    record.freight_in = freight_in

    @api.depends('partner_id')
    def _compute_freight_out(self):
        freight_cost = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.freight_out_cost', 220))
        for record in self:
            record.freight_out = freight_cost

    @api.depends('pallets')
    def _compute_in_out(self):
        in_out_cost = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.in_out_cost', 19))
        for record in self:
            record.in_out = in_out_cost * record.pallets


    @api.depends('partner_id')
    def _compute_aduanas(self):            
            mexico_id = self.env['res.country'].search([('code', '=', 'MX')],limit=1).id
            #aduana = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.aduana', 600))
            aduana = 600
            for record in self:
                if record.partner_id: 
                    if record.partner_id.country_id.id == mexico_id:
                        record.customs = aduana

    
    @api.depends('line_ids')
    def _calc_commission_buyer(self):            
        commision_buyer_percentage = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.commission_buyer_percent', 15)) / 100
        commision_saler_percentage = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.commission_saler_percent', .5)) / 100
        for record in self:
            if record.price_type == 'close':
                record.commission_buyer = (sum(line.price_unit * line.quantity for line in record.line_ids))*commision_buyer_percentage
            else:
                ventas_calculadas = sum(line.price_sale_estimate * line.quantity for line in record.line_ids)
                if ventas_calculadas > 0:
                    ganancias_calculadas = ventas_calculadas - (ventas_calculadas * record.commission)
                    ganancias_calculadas = ganancias_calculadas - (ventas_calculadas*commision_saler_percentage)
                    ganancias_calculadas = ganancias_calculadas - record.hidden_cost - record.others - record.in_out - record.boxes_cost - record.customs - record.freight_in - record.freight_out
                    record.commission_buyer = ganancias_calculadas * commision_buyer_percentage

    

    
    @api.depends('partner_id', 'line_ids')
    def _calc_hidden_cost(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        expenses_json = get_param('bid_manager.additional_expense_ids', '[]')
        expense_ids = json.loads(expenses_json)

        # Recuperar los registros desde la base de datos
        expenses = self.env['additional.expense'].browse(expense_ids)

        for record in self:
            if record.quantity > 0 and record.partner_id:
                base_amount = sum(line.price_unit * line.quantity for line in record.line_ids)
                total_extra_costs = sum((base_amount * expense.percentage / 100) for expense in expenses)

                record.hidden_cost = total_extra_costs """


    # @api.depends('partner_id', 'line_ids.quantity')
    # def _compute_boxes_cost(self):
    #     pass
                






# comission vendedores  .005 de la venta
# comission comprador  15
## freight in   en base a la zona costo promedio por zona
## freight out 220 estatico
## aduanas 600 dependiendo si viene mexico y agregar % de inspeccion
## in/out  19 * pallet

# armar una campo para vaciado de costos ocultos extra
# 2% de merma



