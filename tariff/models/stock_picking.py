# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    entry_summary = fields.Char(string="Entry Summary", required=False)

    location_id_usage = fields.Selection(related="location_id.usage")
    location_dest_id_usage = fields.Selection(related="location_dest_id.usage")

    _sql_constraints = [('entry_summary', 'unique(entry_summary)', "El ENTRY SUMMARY debe ser unico y no repetirse")]

    def button_validate(self):
        #validar si es pase a stock, se force llenado de entry summary
        if (self.location_id.id == 9) and (self.location_dest_id.id == 8): #checa que sea trans interna
            if self.group_id:
                purchase_order = self.env['purchase.order'].search([("group_id", "=", self.group_id.id)], limit=1)
                if purchase_order.importacion == 'Si':   #revisar en purchase order si es importacion
                    if not self.entry_summary:     #checa que tenga un entry summary valido 
                        raise UserError("El movimiento requiere ENTRY SUMMARY para ser validado, ya que es importacion ") #% deposit.name )
                    else: 
                        purchase_order.entry_summary = self.entry_summary
        return super(StockPicking, self).button_validate()
