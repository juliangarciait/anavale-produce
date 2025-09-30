from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    repack_count = fields.Integer(string='Repack Lines', compute='_compute_repack_count')

    def _compute_repack_count(self):
        for order in self:
            order.repack_count = self.env['repack.order'].search_count([
                ('sale_line_id', 'in', order.order_line.ids)
            ])

    # def action_create_repack(self):
    #     self.ensure_one()
    #     lines = self.order_line.filtered(lambda l: l.repack_type != 'none' and not l.repack_processed)
    #     if not lines:
    #         raise UserError(_("No lines in this order need repack or all lines are already processed."))
    #     return lines.create_repack_order()
    

    def action_open_repack_wizard(self):
        self.ensure_one()
        return {
            'name': _('Create Repack'),
            'type': 'ir.actions.act_window',
            'res_model': 'repack.create.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    repack_type = fields.Selection([
        ('none', 'No Repack'),
        ('repack', 'Repack'),
        ('peeled', 'Peeled'),
        ('untailed', 'Untailed'),
        ('rot', 'Remove rot')
    ], string='Repack Type', default='', copy=True,
       help="Select the type of repack process needed for this product")
    
    repack_processed = fields.Boolean(string='Repack Created', default=False, copy=False,
                                     help="Technical field to track if a repack has been created")
    
    repack_status = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'In Process'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Repack Status', copy=False, default=False, 
       help="Status of the repack process")
    
    repack_comments = fields.Text(string='Repack Comments')
    
    repack_line_ids = fields.One2many('repack.order', 'sale_line_id', string='Repack Lines')
    
    def open_repack_form(self):
        """Open form view to edit repack fields"""
        self.ensure_one()
        return {
            'name': _('Edit Repack Information'),
            'view_mode': 'form',
            'res_model': 'sale.order.line',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'view_id': self.env.ref('repack_management.view_sale_order_line_repack_form').id,
            'context': {'repack_edit_mode': True},
        }
    
    # def create_repack_order(self):
    #     if not self:
    #         raise UserError(_("No sale order lines selected."))
    #     repack_lines = []
    #     for line in self:
    #         if not line.product_id or line.product_id.tracking != 'lot':
    #             continue
    #         repack_line = self.env['repack.order'].create({
    #             'product_id': line.product_id.id,
    #             'qty_to_repack': line.product_uom_qty,
    #             'process_type': line.repack_type,
    #             'sale_line_id': line.id,
    #             'lot_id': getattr(line, 'lot_id', False).id,
    #             'comments': line.repack_comments,
    #         })
    #         line.write({
    #             'repack_line_ids': [(4, repack_line.id)],
    #             'repack_status': 'draft',
    #             'repack_processed': True,
    #         })
    #         repack_lines.append(repack_line.id)
    #     if not repack_lines:
    #         raise UserError(_("No valid products for repack found in the selected lines."))
    #     return {
    #         'name': _('Repack Lines'),
    #         'view_mode': 'tree,form',
    #         'res_model': 'repack.order.line',
    #         'domain': [('id', 'in', repack_lines)],
    #         'type': 'ir.actions.act_window',
    #     } 