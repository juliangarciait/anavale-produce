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
    price_type = fields.Selection([('abierto','Precio abierto'),
                                   ('cerrado','Precio cerrado')], 
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


class SsttlementsStockPicking(models.Model):
    _inherit = 'stock.picking'

    def settlements_report_button_function(self):
        context = self._context.copy()
        fecha = self.date_order
        var = []
        for i in self.order_line:
            if i.product_id:
                var.append((0, 0,  {"date": fecha, "product_id": i.product_id.id,
                           "product_uom": i.product_uom.id, "price_unit": i.price_unit}))

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