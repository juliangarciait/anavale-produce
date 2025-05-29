from odoo import models, fields, api

class ProductSize(models.Model):
    _name = 'product.size'
    _description = 'Product Size Classification'
    _order = 'sequence, name'
    
    name = fields.Char('Size Name', required=True)
    code = fields.Char('Size Code')
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Size name already exists!"),
        ('code_uniq', 'unique (code)', "Size code already exists!")
    ]


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    can_be_peeled = fields.Boolean('Can be Peeled', default=False, 
        help="Check this if this product can be processed with the 'peeled' method")
    can_be_untailed = fields.Boolean('Can be Untailed', default=False,
        help="Check this if this product can be processed with the 'untailed' method") 