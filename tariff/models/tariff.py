# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import timedelta

class TariffManager(models.Model):
    _name = 'tariff.manager'
    _description = 'Tariff Manager'

    
    purchase_order = fields.Many2one('purchase.order', string='Purchase Order', required=True, ondelete='cascade')
    amount_payable_to_importer = fields.Float(string="Amount Payable From Buyer to Seller", compute="_compute_amount_payable", store=True)
    sale_price_mx  = fields.Float(string="Sale Price of MX Produce", compute="_compute_amount_payable")
    surcharge_to_buyer = fields.Float(string="Surcharge to Buyer for Duty")#, compute="_compute_amount_payable")
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
    dutiable_value = fields.Float(string="(Dutiable Value Including Duties) Adjusted Produce Sales Price")
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
                porcentaje_comision = int(record.purchase_order.porcentaje_comision)
                #datos para calculo de otros datos
                analytic_tag_ids = self.env['account.analytic.tag']
                for lot in lot_ids:
                    tag = lot.analytic_tag_ids.filtered(lambda tag: len(tag.name)>5)
                    if not tag in analytic_tag_ids:
                        analytic_tag_ids += tag
                move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
                freight_in = move_line_ids.filtered(lambda line: line.account_id.id == 1387 and line.move_id.state == 'posted')
                freight_out = move_line_ids.filtered(lambda line: line.account_id.id == 1394 and line.move_id.state == 'posted')
                maneuvers = move_line_ids.filtered(lambda line: line.account_id.id == 1390 and line.move_id.state == 'posted')
                scrap = move_line_ids.filtered(lambda line: line.account_id.id == 1396 and line.move_id.state == 'posted')
                storage = move_line_ids.filtered(lambda line: line.account_id.id == 1395 and line.move_id.state == 'posted')
                aduana_usa = move_line_ids.filtered(lambda line: line.account_id.id == 1393 and line.move_id.state == 'posted')
                aduana_mex = move_line_ids.filtered(lambda line: line.account_id.id == 1392 and line.move_id.state == 'posted')#[]1392
                adjustment = move_line_ids.filtered(lambda line: line.account_id.id == 1378 and line.move_id.state == 'posted')
                boxes = move_line_ids.filtered(lambda line: line.account_id.id == 1509 and line.move_id.state == 'posted')
                logistics = move_line_ids.filtered(lambda line: line.account_id.id == 1516 and line.move_id.state == 'posted')
                freight_in_update = sum([accline.price_subtotal for accline in freight_in])
                freight_out_update = sum([accline.price_subtotal for accline in freight_out])
                maneuvers_update = sum([accline.price_subtotal for accline in maneuvers])
                storage_update = sum([accline.price_subtotal for accline in storage])
                aduana_usa_update = sum([accline.price_subtotal for accline in aduana_usa])
                aduana_mex_update = sum([accline.price_subtotal for accline in aduana_mex])
                boxes_update = sum([accline.debit for accline in boxes])
                logistics_update = sum([accline.debit for accline in logistics])
                scrap_update = sum([accline.price_subtotal for accline in scrap])
                record.us_freight = freight_out_update
                record.foreign_inland_freight = freight_in_update
                record.loading_unloading =  storage_update
                record.inspection_costs = 0
                record.us_custom_brokers = aduana_usa_update
                record.repack = maneuvers_update
                record.dump = scrap_update
                record.expense_allocation = 0
                
                record.assists = boxes_update


                # Calcular sale_price_mx 
                aggregated_data = {}
                sum_real_sales = 0
                for name, qty, qty_invoiced, price, status in sales_data:
                    sum_real_sales += qty_invoiced * price
                    if price in aggregated_data:
                        aggregated_data[price] += qty_invoiced
                    else:
                        aggregated_data[price] = qty_invoiced
                max_price, max_qty = max(aggregated_data.items(), key=lambda x: x[1])
                record.sale_price_mx  = sum(qty for price, qty in aggregated_data.items()) * max_price

                # Calcular sale_price_mx
                # purchase_order_value = sum(line.qty_received* line.price_unit for line in record.purchase_order.order_line)
                # record.sale_price_mx = purchase_order_value

                #Calcula sales_commission
                sales_commission = 0
                for name, qty, qty_invoiced, price, status in sales_data:
                    sales_commission += qty_invoiced * price
                sales_commission =sales_commission * (porcentaje_comision / 100)  #FALTA SACAR % DE COMISION
                record.sales_commission = sales_commission

                #calcular us_freight
                record.total_costs_subtracted = freight_out_update + freight_in_update + storage_update + maneuvers_update + scrap_update + aduana_usa_update + sales_commission
                record.dutiable_value = record.sale_price_mx - record.total_costs_subtracted
                record.duty_payable = record.dutiable_value - (record.dutiable_value / 1.25)
                


                record.surcharge_to_buyer = record.duty_payable
                record.amount_payable_to_importer = record.sale_price_mx + record.duty_payable




            else:
                record.amount_payable_to_importer = 0
                record.sale_price_mx = 0
                record.surcharge_to_buyer = 0

    
 