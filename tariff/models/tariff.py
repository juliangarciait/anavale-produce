# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import timedelta

class TariffManager(models.Model):
    _name = 'tariff.manager'
    _description = 'Tariff Manager'

    
    purchase_order = fields.Many2one('purchase.order', string='Purchase Order', required=True, ondelete='cascade')
    amount_payable_to_importer = fields.Float(string="Amount Payable From Buyer to Seller", compute="_compute_amount_payable", store=True)
    sale_price_mx  = fields.Float(string="Sale Price of MX Produce", compute="_compute_amount_payable")
    surcharge_to_buyer = fields.Float(string="Surcharge to Buyer for Duty", compute="_compute_amount_payable")
    sales_commission = fields.Float(string="Sales Commission", compute="_compute_amount_payable")
    us_freight = fields.Float(string="U.S. Freight & Insurance")
    loading_unloading = fields.Float(string="Loading and unloading costs at the port")
    inspection_costs = fields.Float(string="USDA Inspection Costs")
    repack = fields.Float(string="Repack, Recondition, Grading Costs (Box & Labor)")
    dump = fields.Float(string="Dump or Donation Costs")
    expense_allocation = fields.Float(string="Profit and General Operating Expense Allocation")
    foreign_inland_freight = fields.Float(string="Foreign-inland freight (Requires Through-Bill of Lading)")
    us_custom_brokers = fields.Float(string="U.S. Customs Broker's Fees (No Foreign Brokers Fees Accepted)")
    custom_duties = fields.Float(string="Customs duties, taxes and fees (Other than Antidumping Duty)")
    total_costs_subtracted = fields.Float(string="Total Costs Subtracted from Produce Sales Price")
    assists = fields.Float(string="Packing Costs , if paid by Importer")
    total_costs_added = fields.Float(string="Total Costs Added to Produce Sales Price")
    duties_value = fields.Float(string="(Dutiable Value Including Duties) Adjusted Produce Sales Price")
    duty_payable = fields.Float(string="Duty Paid or Payable")


    @api.depends('purchase_order')
    def _compute_amount_payable(self):
        for record in self:
            if record.purchase_order:
                #variables de errores
                sales_no_invoiced = False
                has_stock = False
                No_liquidacion = False
                #obtener datos necesarios para calculos
                picking_ids = record.purchase_order.picking_ids.filtered(lambda picking: picking.state == 'done') # Se obtinenen pickings de la orden de compra
                lot_ids = self.env["stock.production.lot"]
                for sml in picking_ids.move_line_ids:
                    lot_ids += sml.lot_id
                sale_lines = self.env['sale.order.line'].search([
                    ('lot_id', 'in', lot_ids.ids),('state', '=', 'sale' )
                ])
                # Obtener la lista de cantidades y precios unitarios
                sales_data = [(line.order_id.display_name, line.qty_delivered, line.qty_invoiced, line.price_unit, line.invoice_status) for line in sale_lines]


                # Calcular amount_payable_to_importer
                aggregated_data = {}
                for name, qty, qty_invoiced, price, status in sales_data:
                    if price in aggregated_data:
                        aggregated_data[price] += qty
                    else:
                        aggregated_data[price] = qty
                max_price, max_qty = max(aggregated_data.items(), key=lambda x: x[1])
                record.amount_payable_to_importer = sum(qty for price, qty in aggregated_data.items()) * max_price

                # Calcular sale_price_mx
                purchase_order_value = sum(line.qty_received* line.price_unit for line in record.purchase_order.order_line)
                record.sale_price_mx = purchase_order_value

                #Calcula sales_commission
                sales_commission = 0
                for name, qty, qty_invoiced, price, status in sales_data:
                    sales_commission += qty_invoiced * price
                sales_commission * 0.02
                record.sales_commission = sales_commission

                #calcular us_freight




            else:
                record.amount_payable_to_importer = 0
                record.sale_price_mx = 0

    
 