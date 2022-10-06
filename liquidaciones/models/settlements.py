# -*- encoding: utf-8 -*-

from email.policy import default
from tokenize import String
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SettlementsSaleOrder(models.Model):
    _inherit = 'purchase.order'

    # llave foranea a liquidaciones

   # al darle click al boton abre el formulario

    def settlements_wizard_function(self):

        return {

            'res_model': 'sale.settlements.wizard',
            # 'res_id': self.partner_id.id,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Liquidaciones',
            #'context': {'default_settlements_line_ids': var},
            'view_id': self.env.ref('liquidaciones.selection_settlements_wizard_form').id
        }

  

  

class SettlementsInherit(models.Model):
    _name = 'sale.settlements'

    @api.model
    @api.onchange('total', 'settlement','freight_in','aduana','maneuvers','adjustment','storage','freight_out')
    def _compute_utility(self):
        self.utility=self.total-(self.settlement+self.freight_in+self.aduana+self.maneuvers+self.adjustment+self.storage+self.freight_out)

    @api.model
    @api.onchange('total', 'utility')
    def _compute_utility_percentage(self):
        if self.utility>0 and self.total>0:
            self.utility_percentage=(self.utility/self.total)*100

    @api.model
    @api.onchange('settlements_line_ids', 'settlements_line_ids.total')
    def _get_settlement(self):
        var = []
        for i in self.settlements_line_ids:
                var.append(i.total)
        logging.info('s'*500)
        logging.info(var)
        salesSum = 0
        for x in var:
            logging.info(x)
            if x:
             salesSum = salesSum + float(x)
        self.settlement = salesSum
        
    
    settlements_sale_order_ids = fields.One2many(
        'purchase.order', 'id', 'Lineas de Trabajo')
    settlements_line_ids = fields.One2many(
        'sale.settlements.lines', 'id', 'Lineas de Trabajo')

    total = fields.Float(
        required=True, tracking=True, string="Sales")
    settlement = fields.Float(
        required=True, tracking=True, string="Settlements", default=_get_settlement)
    utility = fields.Float(
        required=True, tracking=True, string="Utility", default=_compute_utility)
    utility_percentage = fields.Float(
        required=True, tracking=True, string="", default=_compute_utility_percentage)
    freight_in  = fields.Float(
        required=True, tracking=True, string="Freight In", default=_compute_utility)
    aduana = fields.Float(
        required=True, tracking=True, string="Aduana", default=_compute_utility)
    maneuvers = fields.Float(
        required=True, tracking=True, string="Maneuvers", default=_compute_utility)
    adjustment = fields.Float(
        required=True, tracking=True, string="Adjustment", default=_compute_utility)
    storage = fields.Float(
        required=True, tracking=True, string="Storage", default=_compute_utility)
    freight_out = fields.Float(
        required=True, tracking=True, string="Freight Out", default=_compute_utility)
    check_maneuvers=fields.Boolean()
    check_adjustment=fields.Boolean()
    check_storage=fields.Boolean()
    check_freight_out=fields.Boolean()
    check_freight_in=fields.Boolean()
    note = fields.Char(required=True, tracking=True, string="Note")
    journey = fields.Char(required=True, tracking=True, string="Journey")
    company = fields.Char(required=True, tracking=True, string="Company")

    @api.model
    @api.onchange('total')
    def _amount_total(self):
        total=0
        for sub in self.settlements_line_ids:
            logging.info(sub)
            #total=total+sub
            


    # Costo del viaje, este lo escribe el usuario
    freight = fields.Float(required=True, tracking=True, string="Flete")

   
    def action_print_report(self):
        appoinments = self.env['sale.settlements'].search_read([])
        data = {
            #'form': self.read()[0],
           # 'appoinments': appoinments
        }
        return self.env.ref('liquidaciones.report_settlement_templates').report_action(self, data=data)


class SettlementsInheritLines(models.Model):
    _name = 'sale.settlements.lines'

    @api.model
    @api.onchange('price_unit', 'box_rec')
    def _compute_amount(self):
        for line in self:
            line.amount = line.price_unit*line.box_rec

    @api.model
    @api.onchange('purcharse_price', 'box_rec')
    def _compute_total(self):
        for line in self:
            line.total = line.purcharse_price*line.box_rec

    date = fields.Datetime(required=True, tracking=True, string="Fecha")
    product_id = fields.Many2one(
        'product.product', required=True, tracking=True, string="Producto")
    product_uom = fields.Many2one(
        'uom.uom', required=True, tracking=True, string="Medida")
    # Este lo escribe el usuario
    box_emb = fields.Integer(
        required=True, tracking=True, string="Cajas Embalaje")
    # Este lo escribe el usuario
    box_rec = fields.Integer(required=True, tracking=True, string="Cajas Rec.")
    price_unit = fields.Float(
        required=True, tracking=True, string="Precio Unitario")
    amount = fields.Float(required=True, tracking=True,
                          string="Importe", readonly=False,  compute='_compute_amount', default=_compute_amount)
    purcharse_price = fields.Float(
        required=True, tracking=True, string="Precio Compra")
    total = fields.Float(required=True,  string="Total", default=_compute_total)

    
