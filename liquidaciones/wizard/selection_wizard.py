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


    def settlements_report_button_function(self):
        
        self._cr.execute("SELECT id FROM stock_picking WHERE origin LIKE '"+self.name+"' AND state LIKE 'done'")
        data = self._cr.fetchone()
        
        self._cr.execute("SELECT lot_id FROM stock_move_line where picking_id="+str(int(data[0])))
        data2 = self._cr.fetchall()

        values = []
        for x in data2:
            self._cr.execute("SELECT id FROM stock_production_lot WHERE id="+str(int(x[0])))
            values.append(self._cr.fetchall())

        values2 = []
        for x in values:
            self._cr.execute("SELECT account_analytic_tag_id FROM account_analytic_tag_stock_production_lot_rel WHERE stock_production_lot_id="+str(int(x[0][0])))
            values2.append(self._cr.fetchall())

        values3= []
        for x in values2:
            self._cr.execute("select id from account_analytic_tag WHERE LENGTH(name)>5")
            values3.append(self._cr.fetchall())    

        sales = []
        for x in values3:
            self._cr.execute("SELECT price_subtotal FROM account_move_line where account_id=38 AND id="+str(int(x[0][0])))
            sales.append(self._cr.fetchall())  

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
            'context': {'default_settlements_line_ids': var},
            'view_id': self.env.ref('liquidaciones.selection_settlements_wizard_form').id
        }

class SsttlementsStockPicking(models.Model):
    _inherit = 'stock.picking'
    

    