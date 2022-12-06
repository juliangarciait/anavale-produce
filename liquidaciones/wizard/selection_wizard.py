# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleSettlementsWizard(models.TransientModel):
    _name = "sale.settlements.wizard"

    sale_settlements_id = fields.Many2one("sale.settlements")
    price_type = fields.Selection([('open','Open price'),
                                   ('close','Closed price')], 
                                   String="Tipo de precio", required=True,
                                   help="Please select a type of price.")
    price_type_check = fields.Selection([('open','Open price'),
                                   ('close','Closed price')], 
                                   String="Tipo de precio", required=True, store=True,
                                   help="Please select a type of price.", default='close')
    maneuvers=fields.Boolean(default=True, String="Maniobras", 
                                   help="Select if you require maneuvers.")
    adjustment=fields.Boolean(default=True, String="Ajuste", 
                                   help="Select if you require adjustment.")  
    storage=fields.Boolean(default=True, String="Storage", 
                                   help="Select if you require storage")                                                              
    freight_out=fields.Boolean(default=True, String="Freight out", 
                                   help="Select if you require freight out.")  
    freight_in=fields.Boolean(default=True, String="Freight in", 
                                   help="Select if you require freight in.")  
    aduana=fields.Boolean(default=True, String="Aduana", 
                                   help="Select if you require aduana.")  


    def settlements_report_button_function(self):
        purchase_ids = self.env.context.get('active_ids', [])
        purchase_rec = self.env['purchase.order'].browse(purchase_ids)
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
        move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
        for tag_id in analytic_tag_ids:
            tag_name += tag_id.name + ' '
        tag_name = tag_name.split("-")
        sales = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.product_id in po_product_ids)
        freight_in = move_line_ids.filtered(lambda line: line.account_id.id == 1387 and line.move_id.state == 'posted')
        freight_out = move_line_ids.filtered(lambda line: line.account_id.id == 1394 and line.move_id.state == 'posted')
        maneuvers = move_line_ids.filtered(lambda line: line.account_id.id == 1390 and line.move_id.state == 'posted')
        storage = move_line_ids.filtered(lambda line: line.account_id.id == 1395 and line.move_id.state == 'posted')
        aduana_usa = move_line_ids.filtered(lambda line: line.account_id.id in [1393,1392] and line.move_id.state == 'posted')
        aduana_mex = []
        adjustment = move_line_ids.filtered(lambda line: line.account_id.id == 1378 and line.move_id.state == 'posted')
        amountVar = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.product_id in po_product_ids and line.move_id.state == 'posted')
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
        aduana_total = aduana_mexSum + aduana_usaSum       
        quant_obj = self.env["stock.quant"] 
        location_id = self.env["stock.location"].search([('usage', '=', 'internal')])
        if str(self.price_type) == 'open':
            for line in purchase_rec.order_line: #3
                stock = 0
                _logger.info(lot_ids.read())
                quants = quant_obj.search([('product_id', '=', line.product_id.id), ('lot_id', 'in', lot_ids.ids), ('location_id', 'in', location_id.ids)])
                stock = sum([q.quantity for q in quants])
                subtotal = subAmount.get(line.product_id.id, False)
                var_price_unit_hidden = line.qty_received and subtotal/line.qty_received or 0
                new_lines.append((0, 0,  {"date": fecha, "product_id": line.product_id.id,
                            "product_uom": line.product_uom.id, "price_unit": var_price_unit_hidden, "price_unit_origin": var_price_unit_hidden,
                            "box_emb":line.product_qty, "box_rec": line.qty_received,
                            "amount": float(var_price_unit_hidden * line.qty_received),
                            "current_stock": stock}))
                product_line.append(line.product_id.id)
        else:
            for line in purchase_rec.order_line: #3
                new_lines.append((0, 0,  {"date": fecha, "product_id": line.product_id.id,
                            "product_uom": line.product_uom.id, "price_unit": line.price_unit, "price_unit_origin": line.price_unit,
                            "box_emb": line.product_qty, "box_rec": line.qty_received,
                            "amount": float(line.qty_received * line.price_unit)}))
                product_line.append(line.product_id.id)
                
        closed_price = self.env['sale.settlements'].search([('order_id', 'in', purchase_ids), ('status', '=', 'close')])
        view_tree = closed_price and 'liquidaciones.view_settlements_tree_no_create' or 'liquidaciones.view_settlements_tree'
        view_form = closed_price and 'liquidaciones.view_settlements_no_create' or 'liquidaciones.view_settlements'
        return {
            'res_model': 'sale.settlements',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'name': 'Liquidaciones',
            'domain': [('order_id', '=', purchase_rec.id)],
            'context': {'default_settlements_line_ids': new_lines,
                        'default_user_res_partner': purchase_rec.user_id and purchase_rec.user_id.partner_id.name or '',
                        'default_date': fecha,
                        'default_total': sum([sale.price_subtotal for sale in sales]),
                        'default_check_maneuvers': self.maneuvers,
                        'default_check_adjustment': self.adjustment,
                        'default_check_storage': self.storage,
                        'default_check_freight_out': self.freight_out,
                        'default_check_freight_in': self.freight_in,
                        'default_check_aduana': self.aduana,
                        'default_note': tag_name[0],
                        'default_journey': tag_name[1],
                        'default_company': str(purchase_rec.partner_id.name),
                        'default_freight_in': freight_inSum,
                        'default_freight_out': freight_outSum,
                        'default_maneuvers': maneuversSum,
                        'default_storage': storageSum,
                        'default_aduana': aduana_total,
                        'default_adjustment': adjustmentSum,
                        'default_freight_in_unic': freight_inSum,
                        'default_freight_out_unic': freight_outSum,
                        'default_maneuvers_unic': maneuversSum,
                        'default_storage_unic': storageSum,
                        'default_aduana_unic': aduana_total,
                        'default_adjustment_unic': adjustmentSum,
                        'default_order_id': purchase_rec.id,
                        'default_price_type': self.price_type,
                        'lot_ids': lot_ids},
                        
                        
            'views': [(self.env.ref(view_tree).id, 'tree'), (self.env.ref(view_form).id, 'form')],
        }


