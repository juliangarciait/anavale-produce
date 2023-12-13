# -*- encoding: utf-8 -*-

from email.policy import default
from tokenize import String
from odoo import models, fields, api
from openerp.exceptions import ValidationError
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

porcentajes = {
    '8': 8.0,
    '9': 9.0,
    '10': 10.0,
    '11': 11.0,
    '12': 12.0,
}

class SettlementsSaleOrder(models.Model):
    _inherit = 'purchase.order'
    settlement_id = fields.Many2one('sale.settlements')
    settlements_status = fields.Selection([('no', 'Sin liquidacion'),('draft', 'Borrador'),('review', 'Review'), ('close', 'Cerrado')], default = 'no')
    settlement_ids = fields.One2many('sale.settlements', 'order_id')
    
    def settlements_wizard_function(self):
        purchase_rec = self
        po_product_ids = [line.product_id for line in purchase_rec.order_line]
        fecha = purchase_rec.date_order
        picking_ids = purchase_rec.picking_ids.filtered(lambda picking: picking.state == 'done') # Se obtinenen pickings de la orden de compra
        lot_ids = self.env["stock.production.lot"]
        for sml in picking_ids.move_line_ids:
            lot_ids += sml.lot_id
        analytic_tag_ids = self.env['account.analytic.tag']
        for lot in lot_ids:
            tag = lot.analytic_tag_ids.filtered(lambda tag: len(tag.name)>5)
            if not tag in analytic_tag_ids:
                analytic_tag_ids += tag
        move_line_ids= self.env['account.move.line']
        tag_name = ''
        #comprobacion de que no haya ventas pendientes de facturar
        sale_lines = self.env['sale.order.line'].search([('lot_id', 'in', lot_ids.ids),('invoice_status', '=', 'to invoice')])
        if len(sale_lines) > 100:  #quite la limitante por mientas
            raise UserError('Hay ventas pendientes de facturar para estos lotes!')
        else:                                                    
            move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
            for tag_id in analytic_tag_ids:
                tag_name += tag_id.name + ' '
            tag_name = tag_name.split("-")
            if len(tag_name) < 2:
                tag_name.append("")
            sales = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.move_id.state == 'posted')
            freight_in = move_line_ids.filtered(lambda line: line.account_id.id == 1387 and line.move_id.state == 'posted')
            freight_out = move_line_ids.filtered(lambda line: line.account_id.id == 1394 and line.move_id.state == 'posted')
            maneuvers = move_line_ids.filtered(lambda line: line.account_id.id == 1390 and line.move_id.state == 'posted')
            storage = move_line_ids.filtered(lambda line: line.account_id.id == 1395 and line.move_id.state == 'posted')
            aduana_usa = move_line_ids.filtered(lambda line: line.account_id.id == 1393 and line.move_id.state == 'posted')
            aduana_mex = move_line_ids.filtered(lambda line: line.account_id.id == 1392 and line.move_id.state == 'posted')#[]1392
            adjustment = move_line_ids.filtered(lambda line: line.account_id.id in (1378, 1377, 1379, 1477) and line.move_id.state == 'posted')
            amountVar = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.product_id in po_product_ids and line.move_id.state == 'posted')
            boxes = move_line_ids.filtered(lambda line: line.account_id.id == 1509 and line.move_id.state == 'posted')
            subAmount = {}
            for line in amountVar:
                salesSum = subAmount.get(line.product_id.id, 0)
                salesSum += line.price_subtotal
                subAmount[line.product_id.id] = salesSum
            product_line = []
            new_lines = []
            freight_inSum = sum([line.price_subtotal for line in freight_in])
            freight_outSum = sum([line.price_subtotal for line in freight_out])
            maneuversSum = sum([line.price_subtotal for line in maneuvers])
            storageSum = sum([line.price_subtotal for line in storage])
            adjustmentSum = sum([line.price_subtotal for line in adjustment])
            aduana_usaSum = sum([line.price_subtotal for line in aduana_usa])
            aduana_mexSum = sum([line.price_subtotal for line in aduana_mex])
            boxes_sum = sum([line.debit for line in boxes])
            aduana_total = aduana_mexSum + aduana_usaSum       
            quant_obj = self.env["stock.quant"] 
            location_id = self.env["stock.location"].search([('usage', '=', 'internal')])
            ventas_update = 0
            invoice_pendientes_update = 0
            if self.tipo_precio == 'variable':
                for line in purchase_rec.order_line: #3
                    stock = 0
                    line_lotes =  self.env['stock.production.lot'].search([('id', 'in', lot_ids.ids),('product_id', '=', line.product_id.id)])
                    line_lotes += self.env['stock.production.lot'].search([('parent_lod_id', 'in', line_lotes.ids)])
                    quants1 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', location_id.ids)])
                    #inicia busqueda de ventas lotes padre e hijo
                    move_lot = self.env['stock.move'].search([('purchase_line_id', '=', line.id),('state','=','done')], limit=1)
                    move_line_lot = self.env['stock.move.line'].search([('move_id', '=', move_lot.id),('state','=','done')], limit=1)
                    line_lot =  self.env['stock.production.lot'].search([('id', '=', move_line_lot.lot_id.id)])
                    line_lot += self.env['stock.production.lot'].search([('parent_lod_id', 'in', line_lot.ids)])
                    ventas_lines_lot_facturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lot.ids),('invoice_status','=','invoiced')])
                    invoice_line_ids = []
                    for lin in ventas_lines_lot_facturadas:
                        invoice_line_ids.extend(lin.invoice_lines.ids)
                    invoice_line_ids = self.env['account.move.line'].search([('id', 'in', invoice_line_ids),('parent_state','!=', 'cancel')]) #,('parent_state','=', 'posted')
                    suma_cantidad_facturada = 0
                    suma_unidades_facturadas = 0
                    suma_unidades_por_facturadas = 0
                    for invoice_lin in invoice_line_ids:
                        if invoice_lin.parent_state == 'posted':
                            suma_cantidad_facturada += invoice_lin.credit
                            suma_unidades_facturadas += invoice_lin.quantity
                        else:
                            suma_unidades_por_facturadas += invoice_lin.quantity
                    ventas_lines_lot_por_facturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lot.ids),('invoice_status','=','to invoice')])
                    for venta_line in ventas_lines_lot_por_facturadas:
                        suma_unidades_por_facturadas += venta_line.qty_to_invoice

                    #
                    #quants = quant_obj.search([('product_id', '=', line.product_id.id), ('lot_id', 'in', lot_ids.ids), ('location_id', 'in', location_id.ids)])
                    stock = sum([q.quantity for q in quants1])
                    sales_pendientes = self.env["sale.order.line"].search([ ('lot_id', 'in', line_lotes.ids), ('invoice_status', '=', 'to invoice')])
                    invoice_pendientes = 0
                    invoice_pendientes = sum([q.qty_to_invoice for q in sales_pendientes])
                    invoice_pendientes_update += invoice_pendientes
                    sales_pendientes = self.env["sale.order.line"].search([ ('lot_id', 'in', line_lotes.ids), ('invoice_status','=','invoiced')])
                    invoice_line_ids1 = []
                    for lin in sales_pendientes:
                        invoice_line_ids1.extend(lin.invoice_lines.ids)
                    invoice_line_ids1 = self.env['account.move.line'].search([('id', 'in', invoice_line_ids1),('parent_state','!=', 'cancel')]) #,('parent_state','=', 'posted')
                    for invoice_lin in invoice_line_ids1:
                        if invoice_lin.parent_state == 'draft':
                            invoice_pendientes_update += invoice_lin.quantity

                    subtotal = subAmount.get(line.product_id.id, False)
                    ventas_update += subtotal
                    print('espera')
                    if line.qty_received > 0 and line.qty_received > stock+invoice_pendientes and suma_unidades_facturadas>0:
                        #var_price_unit_hidden = line.qty_received and subtotal/(line.qty_received-stock-invoice_pendientes) or 0
                        var_price_unit_hidden = line.qty_received and suma_cantidad_facturada/suma_unidades_facturadas or 0
                    else:
                        var_price_unit_hidden = 0
                    new_lines.append((0, 0,  {"date": fecha, "product_id": line.product_id.id,
                                "product_uom": line.product_uom.id, "price_unit": var_price_unit_hidden, "price_unit_origin_rel": var_price_unit_hidden, "price_unit_origin": var_price_unit_hidden,
                                "box_emb":line.product_qty, "box_rec": line.qty_received, "box_sale": suma_unidades_facturadas,
                                "amount": float(suma_cantidad_facturada), "amount_calc": float(suma_cantidad_facturada),
                                "current_stock": stock, "pending_invoice":suma_unidades_por_facturadas, "lot_id":line_lotes[0].id}))
                    product_line.append(line.product_id.id)
            else:
                subtotal = 0
                for line in purchase_rec.order_line:
                    subtotal += subAmount.get(line.product_id.id, False)
                for line in purchase_rec.order_line: #3
                    if line.product_id.type == 'product':
                        line_lotes =  self.env['stock.production.lot'].search([('id', 'in', lot_ids.ids),('product_id', '=', line.product_id.id)])
                        line_lotes += self.env['stock.production.lot'].search([('parent_lod_id', 'in', line_lotes.ids)])

                        #calcular pendiente por facturar
                        move_lot = self.env['stock.move'].search([('purchase_line_id', '=', line.id),('state','=','done')], limit=1)
                        move_line_lot = self.env['stock.move.line'].search([('move_id', '=', move_lot.id),('state','=','done')], limit=1)
                        line_lot =  self.env['stock.production.lot'].search([('id', '=', move_line_lot.lot_id.id)])
                        line_lot += self.env['stock.production.lot'].search([('parent_lod_id', 'in', line_lot.ids)])
                        ventas_lines_lot_facturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lot.ids),('invoice_status','=','invoiced')])
                        invoice_line_ids = []
                        for lin in ventas_lines_lot_facturadas:
                            invoice_line_ids.extend(lin.invoice_lines.ids)
                        invoice_line_ids = self.env['account.move.line'].search([('id', 'in', invoice_line_ids),('parent_state','!=', 'cancel')]) #,('parent_state','=', 'posted')
                        suma_cantidad_facturada = 0
                        suma_unidades_facturadas = 0
                        suma_unidades_por_facturadas = 0
                        for invoice_lin in invoice_line_ids:
                            if invoice_lin.parent_state == 'posted':
                                suma_cantidad_facturada += invoice_lin.credit
                                suma_unidades_facturadas += invoice_lin.quantity
                            else:
                                suma_unidades_por_facturadas += invoice_lin.quantity
                        ventas_lines_lot_por_facturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lot.ids),('invoice_status','=','to invoice')])
                        for venta_line in ventas_lines_lot_por_facturadas:
                            suma_unidades_por_facturadas += venta_line.qty_to_invoice 

                        stock = 0
                        quants = quant_obj.search([('lot_id', 'in', line_lotes.ids), ('location_id', 'in', location_id.ids)])
                        stock = sum([q.quantity for q in quants])
                        new_lines.append((0, 0,  {"date": fecha, "product_id": line.product_id.id,
                                    "product_uom": line.product_uom.id, "price_unit": line.price_unit, "price_unit_origin_rel": line.price_unit,
                                    "box_emb": line.product_qty, "box_rec": line.qty_received, "box_sale": line.qty_received-stock,
                                    "amount": float(line.qty_received * line.price_unit), "amount_calc": float(line.qty_received * line.price_unit),
                                    "current_stock": stock, "pending_invoice":suma_unidades_por_facturadas, "lot_id":line_lotes[0].id}))
                        product_line.append(line.product_id.id)
                    
            closed_price = self.env['sale.settlements'].search([('order_id', 'in', purchase_rec.ids), ('status', '=', 'close')])
            view_tree = closed_price and 'liquidaciones.view_settlements_tree_no_create' or 'liquidaciones.view_settlements_tree'
            view_form = closed_price and 'liquidaciones.view_settlements_no_create' or 'liquidaciones.view_settlements'
            action_data = {
                            'res_model': 'sale.settlements',
                            'type': 'ir.actions.act_window',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'name': 'Liquidaciones',
                            'domain': [('order_id', '=', purchase_rec.id)],
                            'context': {'default_settlements_line_ids': new_lines,
                                        'default_user_res_partner': purchase_rec.user_id and purchase_rec.user_id.partner_id.name or '',
                                        'default_date': fecha,
                                        'default_total': sum([sale.price_subtotal for sale in sales]),
                                        'default_check_maneuvers': True,
                                        'default_check_adjustment': True,
                                        'default_check_storage': True,
                                        'default_check_freight_out': True,
                                        'default_check_freight_in': purchase_rec.Flete_entrada == "si" or False,
                                        'default_check_aduana': purchase_rec.Aduana_US == 'si' or False,
                                        'default_check_aduana_mx': purchase_rec.Aduana_MX == 'si' or False,
                                        'default_note': tag_name[0],
                                        'default_journey': tag_name[1],
                                        'default_company': str(purchase_rec.partner_id.name),
                                        'default_freight_in': freight_inSum,
                                        'default_freight_out': freight_outSum,
                                        'default_maneuvers': maneuversSum,
                                        'default_storage': storageSum,
                                        'default_aduana': aduana_usaSum,
                                        'default_aduana_mex': aduana_mexSum,
                                        'default_adjustment': adjustmentSum,
                                        'default_order_id': purchase_rec.id,
                                        'default_price_type': self.tipo_precio == "variable" and "open" or "close",
                                        'default_check_boxes': purchase_rec.caja == "si" or False,
                                        'default_boxes': boxes_sum,
                                        'lot_ids': lot_ids,
                                        'default_purchase_date': purchase_rec.date_approve,
                                        'default_commission_percentage': porcentajes.get(purchase_rec.porcentaje_comision),
                                        'default_ventas_update':ventas_update,  
                                        'default_freight_update':freight_inSum, 
                                        'default_aduana_update': aduana_total,
                                        'default_storage_update': storageSum,
                                        'default_maneuvers_update': maneuversSum,
                                        'default_adjustment_update': adjustmentSum,
                                        'default_freight_out_update': freight_outSum, 
                                        'default_pending_invoice': invoice_pendientes_update,
                                        'default_boxes_update': boxes_sum,
                                        'default_stock':stock           
                                        },
                'views': [(self.env.ref(view_form).id, 'form')],
            }
            exists_st = self.env['sale.settlements'].search([('order_id', 'in', purchase_rec.ids)])
            if len(exists_st) > 1:
                exists_st = exists_st[0]
            if len(exists_st) >= 1:
                exists_st.ventas_update = ventas_update
                exists_st.freight_update = freight_inSum
                exists_st.aduana_update = aduana_total
                exists_st.storage_update = storageSum
                exists_st.maneuvers_update = maneuversSum
                exists_st.freight_out_update = freight_outSum
                exists_st.adjustment_update = adjustmentSum
                exists_st.stock = stock
                exists_st.pending_invoice = invoice_pendientes_update
                update_stock_value = 0
                update_pending_value = 0
                if stock > 0:
                    for idx, item in enumerate(new_lines):
                        if item[2]['current_stock'] > 0:
                            update_stock_value += exists_st.settlements_line_ids[idx].current_stock_price * item[2]['current_stock'] 
                    #calculo de valor stock
                if invoice_pendientes_update > 0:
                    for idx, item in enumerate(new_lines):
                        if item[2]['pending_invoice'] > 0:
                            update_pending_value += exists_st.settlements_line_ids[idx].pending_invoice_price * item[2]['pending_invoice'] 
                    #calcular pendiente de invoice
                exists_st.stock_value = update_stock_value
                exists_st.pending_invoice_value = update_pending_value
                action_data.update({"context": {'default_ventas_update':float(subtotal)-adjustmentSum}, "res_id": exists_st.id})
            return action_data
    
    def create_invoice(self):
        for order in self:
            invoice_vals = {
                'partner_id': order.partner_id.id,
                'type': 'in_invoice',  # Factura de compra
                'purchase_id': order.id,
                # Agrega más campos necesarios para la factura
                # ...
            }
            new_invoice = self.env['account.move'].create(invoice_vals)
            bill_union = self.env['purchase.bill.union'].search([('purchase_order_id', '=', order.id)])
            new_invoice.purchase_vendor_bill_id = bill_union
            new_invoice._onchange_purchase_auto_complete()

 
class SettlementsInherit(models.Model):
    _name = 'sale.settlements'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def close_settlements(self):
        self.write({'status': 'close'})
        self.order_id.write({'settlements_status': 'close'})
        if self.price_type == 'open':
            purchase = self.order_id
            total = 0
            total_lineas = 0
            total_units = 0
            total_cost = 0
            total_cost += self.check_storage and self.storage or 0
            total_cost += self.check_maneuvers and self.maneuvers or 0
            total_cost += self.check_adjustment and self.adjustment or 0
            total_cost += self.check_others and self.others or 0
            total_cost += self.check_boxes and self.boxes or 0
            total_cost += self.check_freight_out and self.freight_out or 0
            total_cost += self.check_freight_in and self.freight_in or 0
            total_cost += self.check_aduana and self.aduana or 0
            total_cost += self.check_aduana_mx and self.aduana_mex or 0
            for settlementline in self.settlements_line_ids:
                total_units += settlementline.box_rec
            costo_caja = total_cost / total_units
            for line in purchase.order_line:
                for settlementline in self.settlements_line_ids:
                    if line.product_id == settlementline.product_id and line.product_uom == settlementline.product_uom:
                        line.price_unit = (settlementline.total - (settlementline.box_rec * costo_caja) ) / settlementline.box_rec
                        total += settlementline.total
                        total_lineas += line.price_subtotal
            purchase.create_invoice()
            factura =[]
            for bill in purchase.invoice_ids:
                if bill.state == 'draft':
                    factura = bill
            if total - total_cost < total_lineas:
                print("falto")
                
            elif total - total_cost > total_lineas: 
                print("sobro")
            else: print("igual")
             
    
    def draft_settlements(self):
        self.write({'status': 'draft'})
        self.order_id.write({'settlements_status': 'draft'})

    
    def review_settlements(self):
        self.write({'status': 'review'})
        self.order_id.write({'settlements_status': 'review'})

    purchase_date = fields.Datetime()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    settlements_sale_order_ids = fields.One2many(
        'purchase.order', 'settlement_id', 'Lineas de Trabajo', tracking=True)
    settlements_line_ids = fields.One2many(
        'sale.settlements.lines', 'settlement_id', 'Lineas de Trabajo', tracking=True)
    total = fields.Float(
         tracking=True, string="Sales")
    calculated_sales = fields.Float(
         tracking=True, string="Caculated Sales")#,default=_compute_calculated_sales)
    settlement = fields.Float(
         tracking=True, string="Liquidaciones")#, default=_get_settlement)
    commission_percentage = fields.Float(
         tracking=True, string="Commission Percentage")
    commission = fields.Float(
         tracking=True, string="Commission")
    recommended_price = fields.Float(
         tracking=True, string="Precio Recomendado")#, default=_get_recommended_price)
    utility = fields.Float(
         tracking=True, string="Utility")
    utility_percentage = fields.Float(
         tracking=True, string="")
    freight_in  = fields.Float(
         tracking=True, string="Freight In")#, default=_get_freight_in)
    date = fields.Datetime(tracking=True, string="Fecha", store=True)
    aduana = fields.Float(
         tracking=True, string="Aduana")#, default=_get_aduana)
    aduana_mex = fields.Float(
         tracking=True, string="Aduana MX")
    maneuvers = fields.Float(
        tracking=True, string="Maneuvers")#, default=_get_maneuvers)
        #duplico el campo, pues es necesario maniobras su total y que no sea modificado, lo mismo para los otros dos campos duplicados
    adjustment = fields.Float(
         tracking=True, string="Adjustment")
    storage = fields.Float(
         tracking=True, string="Storage")
    freight_out = fields.Float(
         tracking=True, string="Freight Out")
    freight_total = fields.Float(
         tracking=True, string="Freight")#, compute="_get_freight_total")
    aduana_total = fields.Float(
         tracking=True, string="Aduana")#, compute="_get_aduana_total")
    res_total = fields.Float(
         tracking=True, string="Aduana")
    total_total = fields.Float(
         tracking=True, string="Total")#, compute="_get_total_total")
    total_amount = fields.Float(
         tracking=True, string="Total")
    total_subtotal = fields.Float(
         tracking=True, string="SubTotal")#, compute="_get_subtotal_total")
    storage_total = fields.Float(
         tracking=True, string="Storage", )
    adjustment_total = fields.Float(
         tracking=True, string="Adjustment")
    maneuvers_total = fields.Float(
         tracking=True, string="Maneuvers")
    price_type = fields.Selection([('open','Open price'),
                                   ('close','Closed price')], 
                                   String="Tipo de precio", required=True,
                                   help="Please select a type of price.")
    status = fields.Selection([('draft', 'Borrador'),('review', 'Review'),
                                   ('close','Cerrado')], required=True, default = 'draft')
    check_maneuvers=fields.Boolean()
    check_adjustment=fields.Boolean()
    check_storage=fields.Boolean()
    check_freight_out=fields.Boolean()
    check_freight_in=fields.Boolean()
    check_aduana=fields.Boolean()
    check_aduana_mx = fields.Boolean()
    boxes = fields.Float()
    check_boxes = fields.Boolean()
    ajuste_precio=fields.Float(
         tracking=True, string="Ajuste de precio")
    note = fields.Char(tracking=True, string="Note")
    journey = fields.Char( tracking=True, string="Lote")
    company = fields.Char( tracking=True, string="Company")
    user_res_partner = fields.Char( tracking=True, string="Comprador")
    box_emb_total = fields.Integer(
        tracking=True, string="Cajas Embalaje")
    box_rec_total = fields.Integer(tracking=True, string="Cajas Rec.")
    # Costo del viaje, este lo escribe el usuario
    freight = fields.Float( tracking=True, string="Flete")
    order_id = fields.Many2one("purchase.order")
    others = fields.Float(tracking=True)
    check_others = fields.Boolean(tracking=True)
    total_update = fields.Float( string="Venta Actualizada")
    storage_update = fields.Float( string="Storage Actualizada")
    aduana_update = fields.Float(string="Aduana Actualizada")#, default=_get_aduana)
    aduana_mex_update = fields.Float(string="AduanaMX Actualizada")
    maneuvers_update = fields.Float(string="Maneuvers Actualizada")#, default=_get_maneuvers)
    adjustment_update = fields.Float(string="Adjustment Actualizado")
    freight_out_update = fields.Float(string="Freight Out Actualizado")
    freight_update = fields.Float( string="Flete Actualizado")
    Liquidacion = fields.Float( string="Flete Actualizado")
    ventas_update = fields.Float(string="Ventas Actualizado")
    boxes_update = fields.Float(string="Boxes Actualizado")
    stock = fields.Integer(string="Stock Pendiente")
    stock_value = fields.Integer(string="Stock Pendiente valor")
    pending_invoice = fields.Integer(string="Facturas Pendiente")
    pending_invoice_value = fields.Integer(string="Facturas Pendiente valor")
    check_manual_price=fields.Boolean(string="Precio Manual")
    actualizacion = fields.Boolean(default=True)





    @api.onchange(
            "storage", "check_storage", "maneuvers", "check_maneuvers",
            "adjustment", "check_adjustment", "ajuste_precio", "others",
            "check_others", "commission_percentage", "check_boxes", "boxes",
            "freight_out", "check_freight_out", "freight_in", "check_freight_in",
            "total", "aduana", "check_aduana", "aduana_mex", "check_aduana_mx")
    def _update_lines(self):
        if self.check_manual_price == False:
            _logger.info("Entra a update_lines")
            total_cost = unit_cost = 0
            total_cost += not self.check_storage and self.storage or 0
            total_cost += not self.check_maneuvers and self.maneuvers or 0
            total_cost += not self.check_adjustment and self.adjustment or 0
            total_cost += not self.check_others and self.others or 0
            total_cost += not self.check_boxes and self.boxes or 0
            total_cost += not self.check_freight_out and self.freight_out or 0
            total_cost += not self.check_freight_in and self.freight_in or 0
            total_cost += not self.check_aduana and self.aduana or 0
            total_cost += not self.check_aduana_mx and self.aduana_mex or 0
            total_box = sum([line.box_rec for line in self.settlements_line_ids if (line.amount + line.stock_value) > 0])
            #total_box = sum([line.box_rec for line in self.settlements_line_ids])
            #saber si alguna linea no tiene amount 0 para no cargarle nada

            unit_cost = (total_cost/total_box) if total_box != 0 else 0
            if self.price_type == "open":
                for line in self.settlements_line_ids:
                    if line.price_unit > 0 and line.amount_calc >0:
                        #line.price_unit = line.price_unit_origin_rel - unit_cost - self.ajuste_precio
                        ##line.amount = line.price_unit * line.box_rec
                        #line.commission_rel = line.amount * (self.commission_percentage/100)
                        #line.commission = line.amount * (self.commission_percentage/100)
                        line.deducciones = unit_cost * line.box_rec
                        line._get_amount_calc()
                        
                    else:
                        line.price_unit = 0
                        line.amount = 0
                        line.commission_rel = 0
                        line.commission = 0
            self.storage_total = self.check_storage and self.storage or 0
            self.maneuvers_total = self.check_maneuvers and self.maneuvers or 0
            self.adjustment_total = self.check_adjustment and self.adjustment or 0

    #@api.depends('settlements_line_ids')
    def _get_subtotal_total(self):
        _logger.info("Entra a _get_subtotal_total")
        subtotal = sum([ line.total for line in self.settlements_line_ids])
        self.total_subtotal = subtotal
        if self.price_type == "close":
            self.settlement = sum([line.amount for line in self.settlements_line_ids])
    
    @api.onchange('freight_out', 'check_freight_out', 'freight_in', 'check_freight_in')
    def _get_freight_total(self):
        freight_total = 0
        freight_total += self.check_freight_out and self.freight_out or 0
        freight_total += self.check_freight_in and self.freight_in or 0
        self.freight_total = freight_total
    
    @api.onchange('aduana', 'check_aduana', 'aduana_mex', 'check_aduana_mx')
    def _get_aduana_total(self):
        aduana_total = 0 
        aduana_total += self.check_aduana and self.aduana or 0 
        aduana_total += self.check_aduana_mx and self.aduana_mex or 0
        self.aduana_total = aduana_total

    @api.onchange('storage','check_storage', 'check_maneuvers', 'maneuvers')
    def _get_storage_total(self):
        storage_total = 0 
        maneuvers_total = 0
        storage_total += self.check_storage and self.storage or 0 
        maneuvers_total += self.check_maneuvers and self.maneuvers or 0
        self.storage_total = storage_total
        self.maneuvers_total = maneuvers_total
    
    def _get_total_total(self):
        cost = self.storage_total
        cost += self.maneuvers_total
        cost += self.adjustment_total
        cost += self.others
        self.total_total = self.total_subtotal - self.aduana_total - self.freight_total - cost
    
    def _get_commission(self):
        if self.commission_percentage >= 0 and self.commission_percentage < 101:
            self.commission = (self.commission_percentage/100) * self.total
        else:
            raise ValidationError(('Enter Value Between 0-100.'))
    
    def _compute_utility_percentage(self):
        utility_percentage = 0
        if self.price_type == "open":
            self.utility = self.total_total
            if self.utility > 0 and self.total > 0:
                utility_percentage = (self.utility/self.total) * 100
        else:
            self.utility = self.total - (self.settlement + self.freight_in + self.aduana + self.maneuvers + self.adjustment + self.storage + self.freight_out)
            if self.utility > 0 and self.total > 0:
                utility_percentage = self.total != 0 and ((self.utility/self.total) * 100) or 0.0
        self.utility_percentage = utility_percentage

    def calcular_update(self):
        lines = []
        freight_spoilage_total = 0
        box_emb_total = 0
        box_rec_total = 0
        amount_total = 0
        stock_value_calc = 0
        pendiente_value_calc = 0
        for line in self.settlements_line_ids:
            #calculo de stock value y por facturar value
            quant_obj = self.env["stock.quant"] 
            location_id = self.env["stock.location"].search([('usage', '=', 'internal')])
            line_lotes =  self.env['stock.production.lot'].search([('id', '=', line.lot_id.id)])
            line_lotes += self.env['stock.production.lot'].search([('parent_lod_id', 'in', line_lotes.ids)])
            quants1 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', location_id.ids)])
            stock1 = sum([q.quantity for q in quants1])
            line.stock_value = stock1 * line.current_stock_price
            stock_value_calc += line.stock_value

            sales_pendientes = self.env["sale.order.line"].search([ ('lot_id', 'in', line_lotes.ids), ('invoice_status', '=', 'to invoice')])
            invoice_pendientes = 0
            invoice_pendientes_update = 0
            invoice_pendientes = sum([q.qty_to_invoice for q in sales_pendientes])
            invoice_pendientes_update += invoice_pendientes
            sales_pendientes = self.env["sale.order.line"].search([ ('lot_id', 'in', line_lotes.ids), ('invoice_status','=','invoiced')])
            invoice_line_ids1 = []
            for lin in sales_pendientes:
                invoice_line_ids1.extend(lin.invoice_lines.ids)
            invoice_line_ids1 = self.env['account.move.line'].search([('id', 'in', invoice_line_ids1),('parent_state','!=', 'cancel')]) #,('parent_state','=', 'posted')
            for invoice_lin in invoice_line_ids1:
                if invoice_lin.parent_state == 'draft':
                    invoice_pendientes_update += invoice_lin.quantity
            pendiente_value_calc += invoice_pendientes_update * line.pending_invoice_price
        self.stock_value = stock_value_calc
        self.pending_invoice_value = pendiente_value_calc



    def action_print_report(self):
        lines = []
        freight_spoilage_total = 0
        box_emb_total = 0
        box_rec_total = 0
        amount_total = 0
        stock_value_calc = 0
        pendiente_value_calc = 0
        for line in self.settlements_line_ids: 

            #calculo de stock value y por facturar value
            quant_obj = self.env["stock.quant"] 
            location_id = self.env["stock.location"].search([('usage', '=', 'internal')])
            line_lotes =  self.env['stock.production.lot'].search([('id', '=', line.lot_id.id)])
            line_lotes += self.env['stock.production.lot'].search([('parent_lod_id', 'in', line_lotes.ids)])
            quants1 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', location_id.ids)])
            stock1 = sum([q.quantity for q in quants1])
            line.stock_value = stock1 * line.current_stock_price
            stock_value_calc += line.stock_value

            sales_pendientes = self.env["sale.order.line"].search([ ('lot_id', 'in', line_lotes.ids), ('invoice_status', '=', 'to invoice')])
            invoice_pendientes = 0
            invoice_pendientes_update = 0
            invoice_pendientes = sum([q.qty_to_invoice for q in sales_pendientes])
            invoice_pendientes_update += invoice_pendientes
            sales_pendientes = self.env["sale.order.line"].search([ ('lot_id', 'in', line_lotes.ids), ('invoice_status','=','invoiced')])
            invoice_line_ids1 = []
            for lin in sales_pendientes:
                invoice_line_ids1.extend(lin.invoice_lines.ids)
            invoice_line_ids1 = self.env['account.move.line'].search([('id', 'in', invoice_line_ids1),('parent_state','!=', 'cancel')]) #,('parent_state','=', 'posted')
            for invoice_lin in invoice_line_ids1:
                if invoice_lin.parent_state == 'draft':
                    invoice_pendientes_update += invoice_lin.quantity
            pendiente_value_calc += invoice_pendientes_update * line.pending_invoice_price

            display_name = line.product_id.display_name.replace(
                ")", "").split("(")
            variant = len(display_name) > 1 and display_name[1]
            if self.price_type == 'open':
                data_lines = {
                    'product': line.product_id.name,
                    'product_uom': variant,
                    'box_emb': line.box_emb,
                    'box_rec': line.box_rec,
                    'price_unit': line.price_unit,
                    'amount': line.amount,
                    'freight': line.freight,
                    'spoilage': line.commission,
                    'stock_value': line.stock_value,
                    'total': line.total
                }
                lines.append(data_lines)
                
                self.stock_value = stock_value_calc
                self.pending_invoice_value = pendiente_value_calc

                freight_spoilage_total += line.freight * -1
                
                box_rec_total += line.box_rec
                amount_total += line.amount
            else:
                data_lines = {
                    'product': line.product_id.name,
                    'product_uom': variant,
                    'box_emb': line.box_emb,
                    'box_rec': line.box_rec,
                    'price_unit': line.price_unit_origin,
                    'amount': line.amount,
                    'freight': line.freight,
                    'spoilage': line.commission,
                    'stock_value': line.stock_value,
                    'total': line.amount
                }
                lines.append(data_lines)
                
                self.stock_value = stock_value_calc
                self.pending_invoice_value = pendiente_value_calc

                freight_spoilage_total += line.freight * -1
                
                box_rec_total += line.box_rec
                amount_total += line.amount
        storage_liquidacion = 0
        flete_liquidacion = 0
        aduana_liquidacion = 0
        if self.check_storage == True:
            storage_liquidacion = self.storage
        if self.check_others == True:
            storage_liquidacion += self.others
        if self.check_freight_in == True:
            flete_liquidacion = self.freight_in
        if self.check_aduana == True:
            aduana_liquidacion = self.aduana_total

        
            
        data = {
            'company': self.company,
            'sales': self.total,
            'freight_in': self.freight_in,
            'aduana': self.aduana_total,
            'maneuvers': self.maneuvers_total,
            'adjustment': self.adjustment,
            'storage': storage_liquidacion,
            'freight_out': self.freight_out,
            'utility': self.utility,
            'utility_percentage': self.utility_percentage,
            'date': self.date,
            'freight_spoilage_total': freight_spoilage_total,
            'lines': lines,
            'box_emb_total': box_emb_total,
            'box_rec_total': box_rec_total,
            'amount_total': amount_total,
            'freight_total': self.freight_total,
            'total': self.total_total,
            'commission_percentage': self.commission_percentage,
            'commission_total': self.commission,
            'note': self.note,
            'viaje': self.journey,
            'boxes': self.boxes,
            'ventas_update':self.ventas_update,
            'freight_update': self.freight_update,
            'adjustment_update': self.adjustment_update,
            'aduana_update': self.aduana_update,
            'storage_update': self.storage_update,
            'maneuvers_update':self.maneuvers_update,
            'freight_out_update':self.freight_out_update,
            'boxes_update':self.boxes_update,
            'stock_value':self.stock_value,
            'pending_invoice_value': self.pending_invoice_value

        }
        return self.env.ref('liquidaciones.xlsx_utlity_report2').with_context(
            landscape=True).report_action(self, data=data)
    

    def action_print_report_noupdate(self):
        self.actualizacion == False
        lines = []
        freight_spoilage_total = 0
        box_emb_total = 0
        box_rec_total = 0
        amount_total = 0
        for line in self.settlements_line_ids: 
            display_name = line.product_id.display_name.replace(
                ")", "").split("(")
            variant = len(display_name) > 1 and display_name[1]
            data_lines = {
                'product': line.product_id.name,
                'product_uom': variant,
                'box_emb': line.box_emb,
                'box_rec': line.box_rec,
                'price_unit': line.price_unit,
                'amount': line.amount,
                'freight': line.freight,
                'spoilage': line.commission,
                'stock_value': line.stock_value,
                'total': line.total
            }
            lines.append(data_lines)
            
            freight_spoilage_total += line.freight * -1
            
            box_rec_total += line.box_rec
            amount_total += line.amount
        storage_liquidacion = 0
        flete_liquidacion = 0
        aduana_liquidacion = 0
        if self.check_storage == True:
            storage_liquidacion = self.storage
        if self.check_others == True:
            storage_liquidacion += self.others
        if self.check_freight_in == True:
            flete_liquidacion = self.freight_in
        if self.check_aduana == True:
            aduana_liquidacion = self.aduana_total

        
            
        data = {
            'company': self.company,
            'sales': self.total,
            'freight_in': self.freight_in,
            'aduana': self.aduana_total,
            'maneuvers': self.maneuvers_total,
            'adjustment': self.adjustment,
            'storage': storage_liquidacion,
            'freight_out': self.freight_out,
            'utility': self.utility,
            'utility_percentage': self.utility_percentage,
            'date': self.date,
            'freight_spoilage_total': freight_spoilage_total,
            'lines': lines,
            'box_emb_total': box_emb_total,
            'box_rec_total': box_rec_total,
            'amount_total': amount_total,
            'freight_total': self.freight_total,
            'total': self.total_total,
            'commission_percentage': self.commission_percentage,
            'commission_total': self.commission,
            'note': self.note,
            'viaje': self.journey,
            'boxes': self.boxes,
            'ventas_update':self.ventas_update,
            'freight_update': self.freight_update,
            'adjustment_update': self.adjustment_update,
            'aduana_update': self.aduana_update,
            'storage_update': self.storage_update,
            'maneuvers_update':self.maneuvers_update,
            'freight_out_update':self.freight_out_update,
            'boxes_update':self.boxes_update

        }
        return self.env.ref('liquidaciones.xlsx_utlity_report_noupdate').with_context(
            landscape=True).report_action(self, data=data)
        #return self.env['report.liquidaciones.xlsx_utility_report'].report_action(self, data=data)#(objects=self.settlements_sale_order_ids)


class SettlementsInheritLines(models.Model):
    _name = 'sale.settlements.lines'
    
    # def write(self, vals): 
    #     #if vals: 
    #      #   message = self.get_message(vals)
    #      #   self.settlement_id.message_post(body=message, subject="Lines change")
    #     #res = super(SettlementsInheritLines, self).write(vals)
    #     #return res
    
    # def get_message(self, vals): 
    #     message = '<ul>'
    #     for val in vals: 
    #         message += '<li>(%s) %s: %s -> %s</li>' % (self.product_id.name, self._fields[val].string, self[val], vals[val])
    #     message += '</ul>'
        
    #     return message

    date = fields.Datetime(tracking=True, string="Fecha")
    product_id = fields.Many2one(
        'product.product',  tracking=True, string="Producto",store= True)
    product_uom = fields.Many2one(
        'uom.uom',  tracking=True, string="Medida")
    # Este lo escribe el usuario
    box_emb = fields.Integer(
        tracking=True, string="Cajas Embalaje")
    # Este lo escribe el usuario
    box_rec = fields.Integer(tracking=True, string="Cajas Rec.")
    current_stock = fields.Float(tracking=True, string="Stock")
    pending_invoice = fields.Float(tracking=True, string="PorFacturar")
    box_sale = fields.Integer(tracking=True, string="Cajas Vendidas")
    current_stock_price = fields.Float(tracking=True, string="StockPrice")
    pending_invoice_price = fields.Float(tracking=True, string="PorfactPrice")
    price_unit = fields.Float(
        tracking=True, string="PrecioFinal")
    price_unit_origin = fields.Float(
        tracking=True, string="PrecioFinal1")
    price_unit_origin_rel = fields.Float(related="price_unit_origin", readonly=False)
    price_unit_final = fields.Float(tracking=True, string="PrecioFinalCalc") 
    amount = fields.Float(tracking=True,
                          string="ImporteOrig") 
    amount_calc = fields.Float(tracking=True,
                          string="ImporteCalc") 
    freight = fields.Float(tracking=True,
                          string="Freight")
    deducciones  = fields.Float(tracking=True,
                          string="Deducciones")
    aduanas = fields.Float(tracking=True,
                          string="Aduanas") 
    commission = fields.Float(
        tracking=True, string="Comission")
    total = fields.Float(string="Total", tracking=True)
    commission_rel = fields.Float(
        tracking=True, string="Comission", related="commission",readonly=False)
    settlement_id = fields.Many2one('sale.settlements')
    stock_value = fields.Float()
    pending_invoice_value = fields.Float()
    lot_id = fields.Many2one('stock.production.lot', string='Lot')

    @api.onchange('current_stock_price')
    def _calculate_value(self):
        if self.settlement_id.price_type != "close":
            for line in self:
                stock_val = 0
                stock_val = line.current_stock * line.current_stock_price
                line.stock_value = stock_val
        
    @api.onchange('pending_invoice_price')
    def _calculate_pending_value(self):
        if self.settlement_id.price_type != "close":
            for line in self:
                pending_invoice_value1 = 0
                pending_invoice_value1 = line.pending_invoice * line.pending_invoice_price
                line.pending_invoice_value = pending_invoice_value1

    @api.onchange('deducciones', 'stock_value', 'pending_invoice_value',  'amount')
    #@api.depends('deducciones', 'stock_value',  'amount')
    def _get_amount_calc(self):
        for line in self:
            line.amount_calc =line.amount -line.deducciones + line.stock_value + line.pending_invoice_value
            line.price_unit = (line.amount_calc / line.box_rec)
            line._get_commision()
            line._get_amount()




    @api.onchange('commission')
    def _get_amount(self):
        for line in self:
                line.total =line.amount_calc - line.commission

    @api.onchange('amount_calc')
    def _get_commision(self):
        for line in self:
            line.commission =line.amount_calc * (line.settlement_id.commission_percentage/100)

    @api.onchange('amount', 'amount_calc')
    def _get_price_original(self):
        for line in self:
            line.price_unit = (line.amount_calc / line.box_rec)

    @api.onchange('price_unit')
    def _get_price_unit(self):
        for line in self:
            if line.settlement_id.check_manual_price == True:
                line.amount_calc = (line.price_unit * line.box_rec)
