# -*- coding: utf-8 -*-

from dataclasses import Field
from email.policy import default
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

        fecha = purchase_rec.date_order

        var = []
        for i in purchase_rec.order_line:
            if i.product_id:
                var.append((0, 0,  {"date": fecha, "product_id": i.product_id.id,
                                    "product_uom": i.product_uom.id, "price_unit": i.price_unit,
                                    "box_emb":i.product_qty, "box_rec": i.qty_received,
                                    "amount":(i.price_unit*i.qty_received)}))

    #select * from purchase_order_stock_picking_rel where purchase_order_id=3790

        self._cr.execute("SELECT stock_picking_id FROM purchase_order_stock_picking_rel where purchase_order_id="+str(int(purchase_rec.id)))
        datap = self._cr.fetchall()


        values = []
        for x in datap:
            self._cr.execute("SELECT id FROM stock_picking WHERE id="+str(int(x[0]))+" AND state LIKE 'done'")
            data = self._cr.fetchone()
        
        self._cr.execute("SELECT lot_id FROM stock_move_line where picking_id="+str(int(data[0])))
        data2 = self._cr.fetchall()


        values2 = []
        for x in data2:
            self._cr.execute("SELECT account_analytic_tag_id FROM account_analytic_tag_stock_production_lot_rel WHERE stock_production_lot_id="+str(int(x[0])))
            values2.append(self._cr.fetchall())


        
        values3= []
        for x in values2:
            for j in x:
             self._cr.execute("select id from account_analytic_tag WHERE LENGTH(name)>5 and id="+str(int(j[0])))
             values3.append(self._cr.fetchall())    
        
        #filtrar tags repetidos  
        res_list = []
        for i in range(len(values3)):
            if values3[i] not in values3[i + 1:]:
                res_list.append(values3[i])

        values4= []
        for x in res_list:
            for j in x:
                self._cr.execute("SELECT account_move_line_id FROM account_analytic_tag_account_move_line_rel where account_analytic_tag_id="+str(int(j[0])))
                values4.append(self._cr.fetchall())
                self._cr.execute("SELECT name FROM account_analytic_tag WHERE id="+str(int(j[0])))
                tagNote = self._cr.fetchone()


        sales = []
        freight_in = []
        freight_out = []
        maneuvers = []
        storage = []
        aduana_usa = []
        aduana_mex = []
        for x in values4:
            if x:
                for i in x:
                    self._cr.execute("SELECT price_subtotal FROM account_move_line where account_id=38 AND id="+str(int(i[0])))
                    sales.append(self._cr.fetchall()) 
                    self._cr.execute("SELECT price_subtotal FROM account_move_line where account_id=1387 AND id="+str(int(i[0])))
                    freight_in.append(self._cr.fetchall())  
                    self._cr.execute("SELECT price_subtotal FROM account_move_line where account_id=1390 AND id="+str(int(i[0])))
                    maneuvers.append(self._cr.fetchall())  
                    self._cr.execute("SELECT price_subtotal FROM account_move_line where account_id=1395 AND id="+str(int(i[0])))
                    storage.append(self._cr.fetchall())   
                    self._cr.execute("SELECT price_subtotal FROM account_move_line where account_id=1394 AND id="+str(int(i[0])))
                    freight_out.append(self._cr.fetchall())
                    self._cr.execute("SELECT price_subtotal FROM account_move_line where account_id=1393 AND id="+str(int(i[0])))
                    aduana_usa.append(self._cr.fetchall())
                    self._cr.execute("SELECT price_subtotal FROM account_move_line where account_id=1392 AND id="+str(int(i[0])))
                    aduana_mex.append(self._cr.fetchall())        
        
                           
        salesSum = 0
        for x in sales:
            if x:
             salesSum = salesSum + float(x[0][0])

        freight_inSum = 0
        for x in freight_in:
            if x:
             freight_inSum = freight_inSum + float(x[0][0])

        freight_outSum = 0
        for x in freight_out:
            if x:
             freight_outSum = freight_outSum + float(x[0][0])

        maneuversSum = 0
        for x in maneuvers:
            if x:
             maneuversSum = maneuversSum + float(x[0][0])

        storageSum = 0
        for x in storage:
            if x:
             storageSum = storageSum + float(x[0][0])

        aduana_usaSum = 0
        for x in aduana_usa:
            if x:
             aduana_usaSum = aduana_usaSum + float(x[0][0])
        
        aduana_mexSum = 0
        for x in aduana_mex:
            if x:
             aduana_mexSum = aduana_mexSum + float(x[0][0])

        
        aduana_total=aduana_mexSum+aduana_usaSum
        string =str(tagNote[0])

        return {

            'res_model': 'sale.settlements',
            # 'res_id': self.partner_id.id,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'name': 'Liquidaciones',
            'context': {'default_settlements_line_ids': var,
                        'default_total': salesSum,
                        'default_check_maneuvers': self.maneuvers,
                        'default_check_adjustment': self.adjustment,
                        'default_check_storage': self.storage,
                        'default_check_freight_out': self.freight_out,
                        'default_check_freight_in': self.freight_in,
                        'default_check_aduana': self.aduana,
                        'default_note': string[0:3],
                        'default_journey': string[-4:],
                        'default_company': str(purchase_rec.partner_id.name),
                        'default_freight_in': freight_inSum,
                        'default_freight_out': freight_outSum,
                        'default_maneuvers': maneuversSum,
                        'default_storage': storageSum,
                        'default_aduana': aduana_total,
                        'default_price_type': self.price_type},
            'view_id': self.env.ref('liquidaciones.view_settlements').id
        }

class SsttlementsStockPicking(models.Model):
    _inherit = 'stock.picking'
    

    