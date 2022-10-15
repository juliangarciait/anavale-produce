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

        
                

    #select * from purchase_order_stock_picking_rel where purchase_order_id=3790

        self._cr.execute("SELECT stock_picking_id FROM purchase_order_stock_picking_rel where purchase_order_id="+str(int(purchase_rec.id)))
        datap = self._cr.fetchall()


        values = []
        for x in datap:
            self._cr.execute("SELECT id FROM stock_picking WHERE id="+str(int(x[0]))+" AND state LIKE 'done'")
            data = self._cr.fetchone()
        
        self._cr.execute("SELECT lot_id FROM stock_move_line where picking_id="+str(int(data[0])))
        data2 = self._cr.fetchall()
        
        res = []
        for ele in data2:
         if ele[0] is not None :
             res.append(ele)

        logging.info("res"*500)
        logging.info(res)

        values2 = []
        for x in res:
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
        aduana_mex = []
        adjustment = []
        amountVar=[]
        amountVar2=[]
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
                    self._cr.execute("SELECT price_subtotal FROM account_move_line where account_id=1378 AND id="+str(int(i[0])))
                    adjustment.append(self._cr.fetchall())  
                    for j in purchase_rec.order_line:          
                        if j.product_id:
                          self._cr.execute("SELECT product_id,price_subtotal FROM account_move_line where account_id=38 AND id="+str(int(i[0]))+" AND product_id="+str(int(j.product_id)))
                          amountVar.append(self._cr.fetchall()) 
                          self._cr.execute("SELECT product_id FROM account_move_line where account_id=38 AND id="+str(int(i[0]))+" AND product_id="+str(int(j.product_id)))
                          amountVar2.append(self._cr.fetchall())
                          #self._cr.execute("SELECT product_id FROM account_move_line where account_id=38 AND id="+str(int(i[0]))+" AND product_id="+str(int(j.product_id)))
                          #amountVar2.append(self._cr.fetchall())  

        subAmount=[]

        lista_final = [elemento for elemento in amountVar if elemento]
        lista_casifinal2 = [elemento for elemento in amountVar2 if elemento]

        lista_final2 = []
        for i in range(len(lista_casifinal2)):
            if lista_casifinal2[i] not in lista_casifinal2[i + 1:]:
                lista_final2.append(lista_casifinal2[i])

        

        
        for x in lista_final2:
                    salesSum = 0
                    if x:
                        for j in lista_final:
                            if j:
                                if float(x[0][0]) == float(j[0][0]):
                                    salesSum = salesSum + float(j[0][1])

                        subAmount.append([x[0][0],salesSum]) 


        idVar = []
        var = []
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

        adjustmentSum = 0
        for x in adjustment:
            if x:
             adjustmentSum = adjustmentSum + float(x[0][0])

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
        sumBox=0
        for i in purchase_rec.order_line: #3
            if i.product_id:
                sumBox=sumBox+ float(i.qty_received)

        logging.info("price_type"*500)
        logging.info(self.price_type)
        logging.info(self.price_type=='open')
        if str(self.price_type) =='open':
          for i in purchase_rec.order_line: #3
            if i.product_id:
                for x in subAmount: #2
                                                        if float(x[0]) == float(i.product_id.id):
                                                                                if i.product_id.id  not in idVar:
                                                                                  if any(i.product_id.id in code for code in subAmount):
                                                                                    var_price_unit_hidden=float(x[1])/i.qty_received
                                                                                    logging.info(var_price_unit_hidden)
                                                                                    var_res=(maneuversSum+storageSum+adjustmentSum)/sumBox
                                                                                    logging.info(var_res)
                                                                                    var_price_unit_hidden=var_price_unit_hidden-var_res 
                                                                                    logging.info(var_price_unit_hidden)

                                                                                    var.append((0, 0,  {"date": fecha, "product_id": i.product_id.id,
                                                                                                "product_uom": i.product_uom.id, "price_unit": var_price_unit_hidden,
                                                                                                "box_emb":i.product_qty, "box_rec": i.qty_received,
                                                                                                "amount": float(x[1])}))
                                                                                    idVar.append(i.product_id.id)
                                                                                                                                                                                    
                                                        else:
                                                                            
                                                                                        if i.product_id.id  not in idVar:
                                                                                            if not any(i.product_id.id in code for code in subAmount):
                                                                                           #if i.product_id.id  not in subAmount[0]:
                                                                                            #logging.info(subAmount)
                                                                                             var.append((0, 0,  {"date": fecha, "product_id": i.product_id.id,
                                                                                                        "product_uom": i.product_uom.id, "price_unit": i.price_unit,
                                                                                                        "box_emb":i.product_qty, "box_rec":  i.qty_received,
                                                                                                        "amount": 0}))   
                                                                                            
                                                                                             idVar.append(i.product_id.id)
                                                                                             logging.info(var)        
                                                                                             logging.info(i.qty_received)      
        else:
                for i in purchase_rec.order_line: #3
                 if i.product_id:
                                                                                    var.append((0, 0,  {"date": fecha, "product_id": i.product_id.id,
                                                                                                "product_uom": i.product_uom.id, "price_unit":  i.price_unit,
                                                                                                "box_emb":i.product_qty, "box_rec": i.qty_received,
                                                                                                "amount": float(i.qty_received*i.price_unit)}))
                                                                                    idVar.append(i.product_id.id)
                                                                                      


                                                                                   


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
                        'default_adjustment': adjustmentSum,
                        'default_freight_in_unic': freight_inSum,
                        'default_freight_out_unic': freight_outSum,
                        'default_maneuvers_unic': maneuversSum,
                        'default_storage_unic': storageSum,
                        'default_aduana_unic': aduana_total,
                        'default_adjustment_unic': adjustmentSum,
                        'default_price_type': self.price_type},
            'view_id': self.env.ref('liquidaciones.view_settlements').id
        }

class SsttlementsStockPicking(models.Model):
    _inherit = 'stock.picking'
    

    