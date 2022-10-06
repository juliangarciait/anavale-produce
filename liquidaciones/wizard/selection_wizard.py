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


    def settlements_report_button_function(self):
        purchase_ids = self.env.context.get('active_ids', [])
        purchase_rec = self.env['purchase.order'].browse(purchase_ids)

        fecha = purchase_rec.date_order

        var = []
        for i in purchase_rec.order_line:
            if i.product_id:
                var.append((0, 0,  {"date": fecha, "product_id": i.product_id.id,
                                    "product_uom": i.product_uom.id, "price_unit": i.price_unit,
                                    "box_emb":i.product_qty, "box_rec": i.qty_received}))

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
        for x in values4:
            if x:
                for i in x:
                    logging.info('j'*500)
                    logging.info(i)
                    self._cr.execute("SELECT price_subtotal FROM account_move_line where account_id=38 AND id="+str(int(i[0])))
                    sales.append(self._cr.fetchall())  
                           
        salesSum = 0
        for x in sales:
            if x:
             salesSum = salesSum + float(x[0][0])

        

        string =str(tagNote[0])
        logging.info('dfds'*500)
        logging.info(str(purchase_rec.partner_id.name))

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
                        'default_note': string[0:3],
                        'default_journey': string[-4:],
                        'default_company': str(purchase_rec.partner_id.name)},
            'view_id': self.env.ref('liquidaciones.view_settlements').id
        }

class SsttlementsStockPicking(models.Model):
    _inherit = 'stock.picking'
    

    