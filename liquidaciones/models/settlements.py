# -*- encoding: utf-8 -*-

from odoo import models, fields, api
import logging
            
_logger = logging.getLogger(__name__)  

class SettlementsSaleOrder(models.Model):
    _inherit = 'sale.order'

    #llave foranea a liquidaciones
    

   #al darle click al boton abre el formulario
    def settlements_button_function(self):
        context = self._context.copy()
        variable = self.order_line.product_id
        logging.info("x"*500)
        logging.info(variable)
        return {
            'res_model': 'sale.settlements',
            #'res_id': self.partner_id.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'default_producto_id': (0, 0,  { self.order_line.product_id }),
            'view_id': self.env.ref('liquidaciones.view_settlements').id
        }
       


class SettlementsInherit(models.Model):
    _name = 'sale.settlements'

    liquidaciones_sale_order_ids = fields.One2many('sale.order', 'id', 'Lineas de Trabajo')
    liquidaciones_line_ids = fields.One2many('sale.settlements.lines', 'id', 'Lineas de Trabajo')

class SettlementsInheritLines(models.Model):
    _name = 'sale.settlements.lines'


    fecha = fields.Datetime(required=True, tracking=True) 
    producto_id = fields.Many2one('product.product', required=True, tracking=True)
    product_uom = fields.Many2one('uom.uom', required=True, tracking=True)
        #Este lo escribe el usuario
    cajas_emb = fields.Integer(required=True, tracking=True)
    #Este lo escribe el usuario
    cajas_rec = fields.Integer(required=True, tracking=True)
    precio_unit = fields.Float(required=True, tracking=True)
    importe = fields.Float(required=True, tracking=True)
        #Costo del viaje, este lo escribe el usuario
    flete = fields.Float(required=True, tracking=True)
    precio_compra = fields.Float(required=True, tracking=True)
    total = fields.Float(required=True, readonly=True)



         