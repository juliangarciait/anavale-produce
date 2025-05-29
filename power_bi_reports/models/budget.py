from odoo import models, fields
from datetime import date

class PurchaseBudget(models.Model):
    _name = 'purchase.budget'
    _description = 'Presupuesto de Compra Mensual'
    _order = 'year desc, month desc'

    product_id = fields.Many2one('product.template', string='Producto', required=True)

    month = fields.Selection([
        ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
        ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
        ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre'),
    ], string='Mes', required=True, default=str(date.today().month))

    year = fields.Integer(string='Año', required=True, default=date.today().year)

    # date_budget = fields.Datetime(string='Fecha presupuesto')

    quantity = fields.Float(string='Cantidad Presupuestada', required=True, default=1.0)

    _sql_constraints = [
        ('unique_budget_per_product_month_year',
         'unique (product_id, month, year)',
         'Solo puede existir un presupuesto por producto, mes y año.')
    ]