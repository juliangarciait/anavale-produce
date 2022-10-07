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
                if self.price_type=="open":
                    var.append(i.total)
                else:
                    var.append(i.amount)
        salesSum = 0
        for x in var:
                if x:
                    salesSum = salesSum + float(x)
        self.settlement = salesSum
        
    @api.model
    @api.onchange('settlements_line_ids', 'settlements_line_ids.total')
    def _get_freight_in(self):
        if not self.check_freight_in:
                self.freight_in=0

    @api.model
    @api.onchange('settlements_line_ids', 'settlements_line_ids.total')
    def _get_maneuvers(self):
        if not self.check_maneuvers:
                self.maneuvers=0
    
    @api.model
    @api.onchange('settlements_line_ids', 'settlements_line_ids.total')
    def _get_adjustment(self):
        if not self.check_adjustment:
                self.adjustment=0

    @api.model
    @api.onchange('settlements_line_ids', 'settlements_line_ids.total')
    def _get_storage(self):
        if not self.check_storage:
                self.storage=0

    @api.model
    @api.onchange('settlements_line_ids', 'settlements_line_ids.total')
    def _get_freight_out(self):
        if not self.check_freight_out:
                self.freight_out=0

    @api.model
    @api.onchange('settlements_line_ids', 'settlements_line_ids.total')
    def _get_aduana(self):
        if not self.check_aduana:
                self.aduana=0


    settlements_sale_order_ids = fields.One2many(
        'purchase.order', 'id', 'Lineas de Trabajo')
    settlements_line_ids = fields.One2many(
        'sale.settlements.lines', 'id', 'Lineas de Trabajo')

    total = fields.Float(
         tracking=True, string="Sales")
    settlement = fields.Float(
         tracking=True, string="Settlements", default=_get_settlement)
    commission_percentage = fields.Float(
         tracking=True, string="Commission Percentage")
    utility = fields.Float(
         tracking=True, string="Utility", default=_compute_utility)
    utility_percentage = fields.Float(
         tracking=True, string="", default=_compute_utility_percentage)
    freight_in  = fields.Float(
         tracking=True, string="Freight In", default=_get_freight_in)
    aduana = fields.Float(
         tracking=True, string="Aduana", default=_get_aduana)
    maneuvers = fields.Float(
        tracking=True, string="Maneuvers", default=_get_maneuvers)
    adjustment = fields.Float(
         tracking=True, string="Adjustment", default=_get_adjustment)
    storage = fields.Float(
         tracking=True, string="Storage", default=_get_storage)
    freight_out = fields.Float(
         tracking=True, string="Freight Out", default=_get_freight_out)
    price_type = fields.Selection([('open','Open price'),
                                   ('close','Closed price')], 
                                   String="Tipo de precio", required=True,
                                   help="Please select a type of price.")
    check_maneuvers=fields.Boolean()
    check_adjustment=fields.Boolean()
    check_storage=fields.Boolean()
    check_freight_out=fields.Boolean()
    check_freight_in=fields.Boolean()
    check_aduana=fields.Boolean()
    note = fields.Char(tracking=True, string="Note")
    journey = fields.Char( tracking=True, string="Journey")
    company = fields.Char( tracking=True, string="Company")

    # Costo del viaje, este lo escribe el usuario
    freight = fields.Float( tracking=True, string="Flete")

   
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
    def _get_amount(self):
        logging.info('kio'*500)
        for line in self:
            line.amount = line.price_unit*line.box_rec

    @api.model
    @api.onchange('purcharse_price', 'box_rec')
    def _get_total(self):
        logging.info('kio'*500)
        for line in self:
            line.total = line.purcharse_price*line.box_rec


    date = fields.Datetime(tracking=True, string="Fecha")
    product_id = fields.Many2one(
        'product.product',  tracking=True, string="Producto")
    product_uom = fields.Many2one(
        'uom.uom',  tracking=True, string="Medida")
    # Este lo escribe el usuario
    box_emb = fields.Integer(
        tracking=True, string="Cajas Embalaje")
    # Este lo escribe el usuario
    box_rec = fields.Integer(tracking=True, string="Cajas Rec.")
    price_unit = fields.Float(
        tracking=True, string="Precio Unitario")
    amount = fields.Float(tracking=True,
                          string="Importe") 
    purcharse_price = fields.Float(
        tracking=True, string="Precio Compra")
    total = fields.Float(string="Total", tracking=True)

    

    
