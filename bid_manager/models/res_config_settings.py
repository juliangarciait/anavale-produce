from odoo import models, fields, api, tools

class BidManagerSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    freight_in_cost = fields.Float(string='Costo de Freight In', config_parameter='bid_manager.freight_in_cost')
    freight_out_cost = fields.Float(string='Costo de Freight Out', config_parameter='bid_manager.freight_out_cost')
    in_out_cost = fields.Float(string='Costo de In/Out', config_parameter='bid_manager.in_out_cost')
    days_calculo_ultimos_dias = fields.Integer(string='Días para cálculo de precios recientes', config_parameter='bid_manager.days_calculo_ultimos_dias')
    commission_buyer_percent = fields.Float(string='Porcentaje Comisión Comprador', config_parameter='bid_manager.commission_buyer_percent')
    commission_seller_percent = fields.Float(string='Porcentaje Comisión Vendedor', config_parameter='bid_manager.commission_seller_percent')

    @api.model
    def set_values(self):
        super(BidManagerSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('bid_manager.freight_in_cost', float(self.freight_in_cost))

    @api.model
    def get_values(self):
        res = super(BidManagerSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['freight_in_cost'] = get_param('bid_manager.freight_in_cost')
        return res