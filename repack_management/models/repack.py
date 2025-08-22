from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import re




class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    can_be_peeled = fields.Boolean(string='Can be Peeled', default=False,
                                help='Check this if this product can be processed with peeling function')
    can_be_untailed = fields.Boolean(string='Can be Untailed', default=False, 
                                   help='Check this if this product can be processed with untailing function')




class RepackLine(models.Model):
    _name = 'repack.order'
    _description = 'Repack Order'
    _order = 'id desc'
    
    product_id = fields.Many2one('product.product', string='Product Variant', required=True)
    lot_id = fields.Many2one('stock.production.lot', string='Source Lot', 
                             domain="[('product_id', '=', product_id)]")
    process_type = fields.Selection([
        ('repack', 'Repack'),
        ('peeled', 'Peeled'),
        ('untailed', 'Untailed')
    ], string='Process Type', default='repack', required=True)
    qty_to_repack = fields.Float(string='Quantity Needed', digits='Product Unit of Measure')
    qty_supplied = fields.Float(string='Quantity Supplied', digits='Product Unit of Measure')
    qty_repacked = fields.Float(string='Repacked Qty (Primary)', digits='Product Unit of Measure', compute='_compute_output_quantities', store=True)
    qty_secondary = fields.Float(string='Secondary Qty', digits='Product Unit of Measure', compute='_compute_output_quantities', store=True)
    qty_scrap = fields.Float(string='Scrap Qty', compute='_compute_qty_scrap', store=True, 
                             digits='Product Unit of Measure')
    line_state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'In Process'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Line Status', default='draft', tracking=True, copy=False)
    sale_line_id = fields.Many2one('sale.order.line', string='Sales Order Line')
    location_id = fields.Many2one('stock.location', string="Location")
    creation_date = fields.Datetime(string='Creation Date', readonly=True)
    processed_date = fields.Datetime(string='Processed Date', readonly=True)
    processed_by = fields.Many2one('res.users', string='Processed By', readonly=True)
    line_ids = fields.One2many('repack.order.line', 'repack_id', string='Output Sublines')
    can_be_peeled = fields.Boolean(related='product_id.can_be_peeled', string='Can be Peeled')
    can_be_untailed = fields.Boolean(related='product_id.can_be_untailed', string='Can be Untailed')
    inventory_id = fields.Many2one('stock.inventory', string='Inventory Adjustment', readonly=True)


    def get_next_reprocess_index(self, base_code):
        Lot = self.env['stock.production.lot']
        
        # Buscar lotes cuyo nombre contiene la base
        lots = Lot.search([('name', 'ilike', base_code)])

        max_r = 0
        pattern = re.compile(r"-R(\d+)$")

        for lot in lots:
            match = pattern.search(lot.name)
            if match:
                r_num = int(match.group(1))
                max_r = max(max_r, r_num)

        return max_r + 1  # siguiente R

    
    @api.depends('line_ids.qty_1', 'line_ids.qty_2')
    def _compute_output_quantities(self):
        for line in self:
            line.qty_repacked = sum(line.line_ids.mapped('qty_1'))
            line.qty_secondary = sum(line.line_ids.mapped('qty_2'))
    
    @api.depends('qty_supplied', 'qty_repacked', 'qty_secondary')
    def _compute_qty_scrap(self):
        for line in self:
            if line.qty_supplied > 0:
                line.qty_scrap = line.qty_supplied - line.qty_repacked - line.qty_secondary
            else:
                line.qty_scrap = 0.0
    
    def action_set_to_process(self):
        if self.line_state != 'draft':
            return
        self.write({'line_state': 'process'})
        # Si es tipo repack, crear sublínea automática con el mismo producto si no existe
        if self.process_type == 'repack' and not self.line_ids.filtered(lambda s: s.product_id == self.product_id):
            self.env['repack.order.line'].create({
                'repack_id': self.id,
                'product_id': self.product_id.id,
                'qty_1': 0.0,
                'qty_2': 0.0,
            })
    
    def action_cancel_line(self):
        if self.line_state == 'done':
            raise UserError(_("Cannot cancel a completed line."))
        self.write({'line_state': 'cancel'})
    
    def action_reset_line(self):
        if self.line_state not in ['cancel', 'process']:
            raise UserError(_("Can only reset from cancel or process state."))
        self.write({'line_state': 'draft'})
    
    def action_process_line(self):
        self.ensure_one()
        if self.line_state != 'process':
            raise UserError(_("Line must be in 'In Process' state to complete it."))
        if not self.qty_supplied:
            raise UserError(_("You must supply a quantity before completing the line."))
        if not self.line_ids:
            raise UserError(_("You must add at least one output line with product and quantity."))
        total_output = self.qty_repacked + self.qty_secondary
        if round(total_output + self.qty_scrap, 2) != round(self.qty_supplied, 2):
            raise UserError(_(
                "Total output quantities plus scrap (%.2f) do not match the supplied quantity (%.2f)"
            ) % (total_output + self.qty_scrap, self.qty_supplied))

        # --- Lógica de creación de lotes y ajuste de inventario ---
        internal_location = self.env['stock.location'].search([('usage', '=', 'internal')])
        StockLot = self.env['stock.production.lot']
        StockInventory = self.env['stock.inventory']
        StockScrap = self.env['stock.scrap']
        created_lots = {}
        original_lot = self.lot_id
        original_lot_name = original_lot.name if original_lot else ''
        original_variant_code = self.product_id.product_template_attribute_value_ids.name or self.product_id.name

        lote = ""
        for tag in self.lot_id.analytic_tag_ids:
            if len(tag.name) > 8:
                lote = tag.name

        repacknumber = self.get_next_reprocess_index(lote)
        lot_padre = self.lot_id.parent_lod_id.id 
        lot_creado = 0
        lote_venta = ''
        quants_lot = self.env['stock.quant'].search([('lot_id', '=', self.lot_id.id),('location_id', 'in', internal_location.ids),('quantity', '>', 0)])
        inventory_lines = []
        for line in self.line_ids:
            for idx, qty in enumerate([line.qty_1, line.qty_2], start=1):
                if qty <= 0:
                    continue
                # Determinar nombre de lote


                if line.product_id.id == 999:
                    lot_name = f"{original_lot_name}#{idx}"
                else:
                    product_size_name = line.product_id.product_template_attribute_value_ids.name
                    product_prefix = line.product_id.lot_code_prefix
                    lot_name = f"{product_prefix}{lote}{product_size_name}#{idx}-R{repacknumber}"
                        
                    vals =({
                        'name': lot_name,
                        'product_id': line.product_id.id,
                        'company_id': self.lot_id.company_id.id,
                        'parent_lod_id': lot_padre if lot_padre else self.lot_id.id,
                        'analytic_tag_ids': [(4, tag.id) for tag in self.lot_id.analytic_tag_ids],
                    })
                    lot_creado = self.env['stock.production.lot'].sudo().create(vals)
                    if (line.product_id.id == self.product_id.id) and idx == 1:
                        lote_venta = lot_creado
                #lot_creado = self.env['stock.production.lot'].browse(lot_creado)
                line.lot_id =  lot_creado
                created_lots[(line.product_id.id, idx)] = lot_creado
                # Preparar línea de inventario
                inventory_lines.append((0, 0, {
                    'company_id': self.lot_id.company_id.id,
                    'product_id': line.product_id.id,
                    'prod_lot_id': lot_creado.id,
                    'product_qty': qty,
                    'location_id': self.location_id.id,
                }))
        # Crear el ajuste de inventario
        inventory = None
        if inventory_lines:

            cantidad_reducida = self.qty_supplied - self.qty_scrap
            
            existencia = sum(line.quantity for line in quants_lot)
            inventory_lines.append((0, 0, {
                    'company_id': self.lot_id.company_id.id,
                    'product_id': self.product_id.id,
                    'prod_lot_id': self.lot_id.id,
                    'product_qty': existencia-cantidad_reducida,
                    'location_id': self.location_id.id,
                }))
            inventory = StockInventory.sudo().create({
                'name': f"Repack Output for Line {self.id}",
                'product_ids': [(4, self.product_id.id)],
                'location_ids': [(4, self.location_id.id)],
                'line_ids': inventory_lines,
            })
            # for line_vals in inventory_lines:
            #     line_vals['inventory_id'] = inventory.id
            #     self.env['stock.inventory.line'].create(line_vals)
            #inventory.sudo().action_start()
            #inventory.line_ids = inventory_lines
            #inventory.sudo().action_validate()
            inventory.action_start()  # En algunos casos, necesario para estados intermedios
            inventory.action_validate()



            self.inventory_id = inventory.id
        # Crear scrap si corresponde
        if self.qty_scrap > 0:
            StockScrap.create({
                'product_id': self.product_id.id,
                'lot_id': self.lot_id.id if self.lot_id else False,
                'scrap_qty': self.qty_scrap,
                'product_uom_id': self.product_id.uom_id.id,
                'origin': f"Repack Line {self.id}",
                'date_done': fields.Datetime.now(),
                'company_id': self.lot_id.company_id.id,
            })
            StockScrap.action_validate()
        self.write({
            'line_state': 'done',
            'processed_date': fields.Datetime.now(),
            'processed_by': self.env.user.id,
        })
        if self.sale_line_id:
            self.sale_line_id.write({'repack_status': 'done'})
            self.sale_line_id.write({'lot_id': lote_venta.id })
        return True


class RepackOrderLine(models.Model):
    _name = 'repack.order.line'
    _description = 'Repack Order line for Output Products'
    _order = 'id desc'
    
    repack_id = fields.Many2one('repack.order', string='Repack Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product Variant', required=True,
                                domain="[('product_tmpl_id', '=', parent_template_id)]")
    parent_template_id = fields.Many2one(related='repack_id.product_id.product_tmpl_id', 
                                        string='Parent Product Template', store=True)
    qty_1 = fields.Float(string='Output Quantity #1', digits='Product Unit of Measure')
    qty_2 = fields.Float(string='Output Quantity #2', digits='Product Unit of Measure')
    lot_id = fields.Many2one('stock.production.lot', string='Created Lot', readonly=True)
    process_type = fields.Selection(related='repack_id.process_type', store=True)
    state = fields.Selection(related='repack_id.line_state', string='Status', store=True)
    _sql_constraints = [
        ('unique_product', 'unique(repack_id, product_id)', 
         'You cannot have two lines with the same product variant!')
    ]
    @api.onchange('repack_id')
    def _onchange_repack_id(self):
        for line in self:
            if line.repack_id and line.repack_id.product_id:
                line.parent_template_id = line.repack_id.product_id.product_tmpl_id.id
    @api.model
    def default_get(self, fields_list):
        res = super(RepackOrderLine, self).default_get(fields_list)
        if 'repack_id' in self.env.context:
            repack_id = self.env.context.get('repack_id')
            if repack_id:
                repack = self.env['repack.order'].browse(repack_id)
                if repack and repack.product_id:
                    res['repack_id'] = repack_id
                    res['parent_template_id'] = repack.product_id.product_tmpl_id.id
        return res 