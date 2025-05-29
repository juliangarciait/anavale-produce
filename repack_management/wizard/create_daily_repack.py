from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CreateDailyRepack(models.TransientModel):
    _name = 'create.daily.repack.wizard'
    _description = 'Create Daily Repack Lines'
    
    date = fields.Date(string='Process Date', default=fields.Date.context_today,
                     required=True, help="Date for the repack lines")
    company_id = fields.Many2one('res.company', string='Company', 
                                default=lambda self: self.env.company)
    
    pending_count = fields.Integer(string='Pending Sales Lines', compute='_compute_pending_counts')
    
    @api.depends('date')
    def _compute_pending_counts(self):
        """Compute number of pending repack lines"""
        self.ensure_one()
        
        # Find pending sales order lines
        count = self.env['sale.order.line'].search_count([
            ('order_id.state', 'in', ['sale', 'done']),
            ('repack_type', '!=', ''),
            ('repack_processed', '=', False)
        ])
        
        self.pending_count = count
    
    def action_create_repack(self):
        """Create a repack order from unprocessed sale order lines"""
        self.ensure_one()
        
        # Find pending sale order lines for repack
        sale_lines = self.env['sale.order.line'].search([
            ('order_id.state', 'in', ['sale', 'done']),
            ('repack_type', '!=', ''),
            ('repack_processed', '=', False)
        ])
        
        if not sale_lines:
            raise UserError(_("No pending sales order lines found for repack."))
        
        repack_lines = []
        for line in sale_lines:
            if not line.product_id or line.product_id.tracking != 'lot':
                continue
            repack_line = self.env['repack.order.line'].create({
                'product_id': line.product_id.id,
                'qty_to_repack': line.product_uom_qty,
                'process_type': line.repack_type,
                'sale_line_id': line.id,
                'lot_id': line.lot_id.id,
            })
            line.write({
                'repack_processed': True,
                'repack_status': 'draft',
                'repack_line_ids': [(4, repack_line.id)],
            })
            repack_lines.append(repack_line.id)
        
        if not repack_lines:
            raise UserError(_("No valid products for repack found in the selected lines."))
        
        # Show created repack lines
        action = {
            'name': _('Created Repack Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'repack.order.line',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', repack_lines)],
            'context': {'create': False},
        }
        
        if len(repack_lines) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': repack_lines[0],
            })
            
        return action 