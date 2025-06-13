from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_locations = fields.Boolean(
        string='Usuario Warehouse Externo',
        help='Si está activo, solo podrá ver movimientos e inventarios de las ubicaciones permitidas.'
    )

    location_ids = fields.Many2many(
        'stock.location',
        'res_users_stock_location_rel',
        'user_id', 'location_id',
        string='Ubicaciones permitidas',
        help='Ubicaciones de almacén a las que el usuario tiene acceso.'
    ) 