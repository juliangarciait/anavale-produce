# -*- encoding: utf-8 -*-

from email.policy import default
from tokenize import String
from odoo import models, fields, api
from openerp.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SettlementsSaleOrder(models.Model):
    _inherit = 'purchase.order'
    settlement_id = fields.Many2one('sale.settlements')
    settlements_status = fields.Selection([('draft', 'Borrador'), ('close', 'Cerrado')], default = 'draft')
    
    def settlements_wizard_function(self):
        return {
            'res_model': 'sale.settlements.wizard',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Liquidaciones',
            'view_id': self.env.ref('liquidaciones.selection_settlements_wizard_form').id
        }

 
class SettlementsInherit(models.Model):
    _name = 'sale.settlements'

    def close_settlements(self):
        self.write({'status': 'close'})
        self.order_id.write({'settlements_status': 'close'})
    
    def draft_settlements(self):
        self.write({'status': 'draft'})
        self.order_id.write({'settlements_status': 'draft'})

    @api.model
    @api.onchange('total', 'settlement','freight_in','aduana','maneuvers','adjustment','storage','freight_out','commission','storage_total','maneuvers_total')
    def _compute_utility(self):
        if self.price_type=="open":
            var = self.commission + self.freight_in+self.aduana+self.maneuvers+self.adjustment+self.storage+self.freight_out
            self.utility=self.total - var
        else:    
            var = self.settlement+self.freight_in+self.aduana+self.maneuvers+self.adjustment+self.storage+self.freight_out
            self.utility=self.total - var

    @api.model
    @api.onchange('total','maneuvers','adjustment','storage','storage_total','maneuvers_total', 'check_storage', 'check_maneuvers', 'check_adjustment')
    def _compute_calculated_sales(self):
        self.calculated_sales=self.total-(self.check_maneuvers and self.maneuvers or 0 + self.check_adjustment and self.adjustment or 0 + self.check_storage and self.storage or 0)

    @api.model
    @api.onchange('total', 'utility')
    def _get_recommended_price(self):
        #obtener el precio redcomendado, pero no se si va en la tabla de abjo o en la tabla de arriba
        if self.utility>0 and self.total>0:
            self.utility_percentage=(self.utility/self.total)*100

    @api.model
    @api.onchange('total', 'utility')
    def _compute_utility_percentage(self):
        if self.utility>0 and self.total>0:
            self.utility_percentage=(self.utility/self.total)*100

    @api.model
    @api.onchange('commission_percentage')
    def _compute_commission_percentage(self):
        if self.commission_percentage > 100 or self.commission_percentage < 0:
            self.commission_percentage=0
            raise ValidationError(('Enter Value Between 0-100.'))
             

    @api.model
    @api.onchange('settlements_line_ids', 'commission_percentage', 'total', 'settlement','freight_in','aduana','maneuvers','maneuvers_total','adjustment','storage','freight_out','storage_total')
    def _get_settlement(self):
        var = []
        for i in self.settlements_line_ids:
            if self.price_type=="open":
                self.settlement = self.calculated_sales-(self.freight_in+self.aduana+self.freight_out+((self.commission_percentage/100)*self.calculated_sales))
            else:
                var.append(i.amount)
                salesSum = 0
                for x in var:
                    if x:
                        salesSum = salesSum + float(x)
                self.settlement = salesSum
        
    @api.model
    @api.onchange('commission_percentage')
    def _get_commission(self):
        if self.commission_percentage >0 and self.commission_percentage<101:
            self.commission = (self.commission_percentage/100)*self.calculated_sales

    @api.model
    @api.onchange( 'check_freight_in')
    def _get_freight_in(self):
        if not self.check_freight_in:
            self.freight_in=0
        else:
            self.freight_in=self.freight_in_unic

    @api.model
    @api.onchange('check_maneuvers')
    def _get_maneuvers(self):
        self.maneuvers=self.maneuvers_unic
        self.maneuvers_total = self.maneuvers_unic

    @api.model
    @api.onchange( 'check_adjustment')
    def _get_adjustment(self):
        self.adjustment=self.adjustment_unic
        self.adjustment_total=self.adjustment_unic

    @api.model
    @api.onchange( 'check_storage')
    def _get_storage(self):
        self.storage=self.storage_unic
        self.storage_total = self.storage_unic

    @api.model
    @api.onchange( 'check_freight_out')
    def _get_freight_out(self):
        if not self.check_freight_out:
            self.freight_out=0
        else:
            self.freight_out=self.freight_out_unic

    @api.model
    @api.onchange( 'freight_out','freight_in')
    def _get_freight_total(self):
        self.freight_total=(self.freight_out+self.freight_in)*-1

    @api.model
    @api.onchange('aduana')
    def _get_aduana_total(self):
        self.aduana_total=(self.aduana)*-1

    @api.model
    @api.onchange('freight_total','aduana_total')
    def _get_res_total(self):
        self.res_total=self.aduana_total+self.freight_total

    @api.model
    @api.onchange('settlements_line_ids')
    def _get_subtotal_total(self):
        subtotal=0
        
        for line in self.settlements_line_ids:
            subtotal=subtotal+line.total
        self.total_subtotal=subtotal
    @api.model
    @api.onchange('aduana_total', 'freight_total','total_subtotal')        
    def _get_total_total(self):
        cost = not self.check_storage and self.storage_total or 0 + (not self.check_maneuvers and self.maneuvers_total or 0) + (not self.check_adjustment and self.adjustment_total)
        self.total_total=self.total_subtotal+self.aduana_total+self.freight_total - cost

    @api.model
    @api.onchange( 'check_aduana')
    def _get_aduana(self):
        if not self.check_aduana:
            self.aduana=0
        else:
            self.aduana=self.aduana_unic
    
    @api.onchange('commission_percentage')
    def _compute_line_commision(self):
        for line in self.settlements_line_ids:
            line.update({'commission': ((line.price_unit*line.box_rec)*(self.commission_percentage/100))})
            line.update({'total': (line.amount-line.commission)})
    

    @api.onchange('ajuste_precio')
    def _compute_line_ajuste_precio(self):
        for line in self.settlements_line_ids:
            new_price_unit = line.price_unit_origin-self.ajuste_precio
            line.update({'price_unit': new_price_unit, 'amount': new_price_unit*line.box_rec,
                'total': (new_price_unit*line.box_rec) - line.commission})


    @api.onchange('calculated_sales')
    def _compute_line_price_unit(self):
        sumBox=0
        sumBox2=0
        for line in self.settlements_line_ids:
               sumBox2 = sumBox2+ float(line.box_rec)
        for line in self.settlements_line_ids:
                sumBox=sumBox+ float(line.box_rec)
        var_res=(self.check_maneuvers and self.maneuvers or 0 + self.check_storage and self.storage or 0 + self.check_adjustment and self.adjustment)/sumBox
        self.box_emb_total =sumBox
        self.box_rec_total = sumBox2
        for line in self.settlements_line_ids:
            if  line.box_rec>0 and sumBox>0:
                line.update({'price_unit': line.price_unit_origin - var_res})
                line.update({'commission': (line.price_unit_origin * line.box_rec) * (self.commission_percentage/100)})
                line.update({'amount': line.price_unit*line.box_rec, 'total': (line.price_unit*line.box_rec) - line.commission})
        amount=0
        for line in self.settlements_line_ids:
            amount=amount+line.amount
        self.total_amount=amount
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    settlements_sale_order_ids = fields.One2many(
        'purchase.order', 'settlement_id', 'Lineas de Trabajo')
    settlements_line_ids = fields.One2many(
        'sale.settlements.lines', 'settlement_id', 'Lineas de Trabajo')
    total = fields.Float(
         tracking=True, string="Sales")
    calculated_sales = fields.Float(
         tracking=True, string="Caculated Sales",default=_compute_calculated_sales)
    settlement = fields.Float(
         tracking=True, string="Liquidaciones", default=_get_settlement)
    commission_percentage = fields.Float(
         tracking=True, string="Commission Percentage")
    commission = fields.Float(
         tracking=True, stored=True, string="Commission", readonly=True)
    recommended_price = fields.Float(
         tracking=True, string="Precio Recomendado", default=_get_recommended_price)
    utility = fields.Float(
         tracking=True, string="Utility", readonly=True)
    utility_percentage = fields.Float(
         tracking=True, string="", readonly=True)
    freight_in  = fields.Float(
         tracking=True, string="Freight In", default=_get_freight_in)
    date = fields.Datetime(tracking=True, string="Fecha", store=True)
    freight_in_unic = fields.Float(
         tracking=True, string="Freight In")
    aduana = fields.Float(
         tracking=True, string="Aduana", default=_get_aduana)
    aduana_unic = fields.Float(
         tracking=True, string="Aduana")
    maneuvers = fields.Float(
        tracking=True, string="Maneuvers", default=_get_maneuvers)
        #duplico el campo, pues es necesario maniobras su total y que no sea modificado, lo mismo para los otros dos campos duplicados
    maneuvers_unic = fields.Float(
        tracking=True, string="Maneuvers", default=_get_maneuvers) 
    adjustment = fields.Float(
         tracking=True, string="Adjustment", default=_get_adjustment)
    adjustment_unic  = fields.Float(
         tracking=True, string="Adjustment")
    storage = fields.Float(
         tracking=True, string="Storage", default=_get_storage)
    storage_unic = fields.Float(
         tracking=True, string="Storage")
    freight_out = fields.Float(
         tracking=True, string="Freight Out", default=_get_freight_out)
    freight_total = fields.Float(
         tracking=True, string="Freight", default=_get_freight_total)
    aduana_total = fields.Float(
         tracking=True, string="Aduana", default=_get_aduana_total)
    res_total = fields.Float(
         tracking=True, string="Aduana", default=_get_res_total)
    total_total = fields.Float(
         tracking=True, string="Total", default=_get_total_total)
    total_amount = fields.Float(
         tracking=True, string="Total")
    total_subtotal = fields.Float(
         tracking=True, string="SubTotal", default=_get_subtotal_total)
    freight_out_unic = fields.Float(
         tracking=True, string="Freight Out")
    storage_total = fields.Float(
         tracking=True, string="Storage")
    adjustment_total = fields.Float(
         tracking=True, string="Adjustment")
    maneuvers_total = fields.Float(
         tracking=True, string="Maneuvers")
    price_type = fields.Selection([('open','Open price'),
                                   ('close','Closed price')], 
                                   String="Tipo de precio", required=True,
                                   help="Please select a type of price.")
    status = fields.Selection([('draft','Borrador'),
                                   ('close','Cerrado')], required=True, default = 'draft')
    check_maneuvers=fields.Boolean()
    check_adjustment=fields.Boolean()
    check_storage=fields.Boolean()
    check_freight_out=fields.Boolean()
    check_freight_in=fields.Boolean()
    check_aduana=fields.Boolean()
    ajuste_precio=fields.Float(
         tracking=True, string="Ajuste de precio")
    note = fields.Char(tracking=True, string="Note")
    journey = fields.Char( tracking=True, string="Journey")
    company = fields.Char( tracking=True, string="Company")
    user_res_partner = fields.Char( tracking=True, string="Comprador")
    box_emb_total = fields.Integer(
        tracking=True, string="Cajas Embalaje")
    box_rec_total = fields.Integer(tracking=True, string="Cajas Rec.")

    # Costo del viaje, este lo escribe el usuario
    freight = fields.Float( tracking=True, string="Flete")

    order_id = fields.Many2one("purchase.order")

   
    def action_print_report(self):
        return self.env.ref('liquidaciones.report_settlement_templates').with_context(landscape=True).report_action(self, data={})


class SettlementsInheritLines(models.Model):
    _name = 'sale.settlements.lines'

    @api.model
    @api.onchange('price_unit', 'box_rec', 'commission')
    def _get_amount(self):
        for line in self:
            line.amount = line.price_unit*line.box_rec
            line.total = (line.price_unit*line.box_rec) - line.commission

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
    current_stock = fields.Float(tracking=True, string="Stock")
    price_unit = fields.Float(
        tracking=True, string="Precio Unitario")
    price_unit_origin = fields.Float(
        tracking=True, string="Precio Unitario")
    amount = fields.Float(tracking=True,
                          string="Importe") 
    freight = fields.Float(tracking=True,
                          string="Freight") 
    aduanas = fields.Float(tracking=True,
                          string="Aduanas") 
    commission = fields.Float(
        tracking=True, string="Comission")
    total = fields.Float(string="Total", tracking=True)
    commission_rel = fields.Float(
        tracking=True, string="Comission", related="commission")
    total_rel = fields.Float(string="Total", tracking=True, related="total")
    settlement_id = fields.Many2one('sale.settlements')
