from odoo import models, fields, api, tools
import json

class AdditionalExpense(models.Model):
    _name = 'additional.expense'
    _description = 'Additional Expense'

    name = fields.Char(string='Nombre', required=True)
    percentage = fields.Float(string='Porcentaje', required=True)
    


class BidManagerSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    freight_in_cost = fields.Float(string='Costo de Freight In', config_parameter='bid_manager.freight_in_cost')
    freight_out_cost = fields.Float(string='Costo de Freight Out', config_parameter='bid_manager.freight_out_cost')
    in_out_cost = fields.Float(string='Costo de In/Out', config_parameter='bid_manager.in_out_cost')
    days_calculo_ultimos_dias = fields.Integer(string='Días para cálculo de precios recientes', config_parameter='bid_manager.days_calculo_ultimos_dias')
    commission_buyer_percent = fields.Float(string='Porcentaje Comisión Comprador', config_parameter='bid_manager.commission_buyer_percent')
    commission_saler_percent = fields.Float(string='Porcentaje Comisión Vendedor', config_parameter='bid_manager.commission_saler_percent')

    additional_expense_ids = fields.Many2many(
        'additional.expense',
        string='Gastos Adicionales'
    )

    @api.model
    def set_values(self):
        """Guarda los valores en ir.config_parameter"""
        super(BidManagerSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        
        freight_in_cost = self.freight_in_cost
        #self.env['ir.config_parameter'].sudo().set_param('bid_manager.freight_in_cost', self.freight_in_cost)
        # Guardar los IDs de los registros seleccionados
        additional_expense_ids = self.additional_expense_ids.ids
        set_param('bid_manager.additional_expense_ids', json.dumps(additional_expense_ids))
        set_param('bid_manager.freight_in_cost', self.freight_in_cost)

    @api.model
    def get_values(self):
        """Carga los valores desde ir.config_parameter"""
        res = super(BidManagerSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param

        res['freight_in_cost'] = float(self.env['ir.config_parameter'].sudo().get_param('bid_manager.freight_in_cost', default=0))
        
        expense_ids_json = get_param('bid_manager.additional_expense_ids', '[]')
        expense_ids = json.loads(expense_ids_json)

        # Restaurar los registros Many2many
        res['additional_expense_ids'] = [(6, 0, expense_ids)]
        return res