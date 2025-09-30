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
        ('untailed', 'Untailed'),
        ('rot', 'Remove rot')
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
    comments = fields.Text(string='Comments')
    bill_id = fields.Many2one('account.move', string='Bill', readonly=True)
    bill_line_id = fields.Many2one('account.move.line', string='Bill Line', readonly=True)

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

    def create_bills(self):
        """Create bills for selected repack orders in done state"""
        # Filter only done repack orders that don't have a bill yet
        done_repacks = self.filtered(lambda r: r.line_state == 'done' and not r.bill_id)
        
        if not done_repacks:
            raise UserError(_("No valid repack orders found. Only 'Done' status orders without existing bills can be processed."))
        
        # Group by company if needed (assuming single company for now)
        AccountMove = self.env['account.move']
        
        # Create the bill
        bill_vals = {
            'type': 'in_invoice',  # Vendor bill
            'partner_id': self.env.company.partner_id.id,  # Use company as vendor for now
            'date': fields.Date.today(),
            'ref': f"Repack Bill",
            'invoice_line_ids': []
        }
        
        # Create invoice lines for each repack order
        for repack in done_repacks:
            if repack.qty_supplied > 0:  # Only create line if there's quantity
                # Get lot analytic tags
                analytic_tag_ids = []
                if repack.lot_id and repack.lot_id.analytic_tag_ids:
                    analytic_tag_ids = [(6, 0, repack.lot_id.analytic_tag_ids.ids)]
                
                line_vals = {
                    'name': repack.lot_id.name if repack.lot_id else f"Repack {repack.id}",
                    'account_id': 1390,  # Fixed account ID as requested
                    'quantity': repack.qty_supplied,
                    'price_unit': 1.0,  # Fixed price as requested
                    'analytic_tag_ids': analytic_tag_ids,
                }
                bill_vals['invoice_line_ids'].append((0, 0, line_vals))
        
        # Create the bill only if there are lines
        if bill_vals['invoice_line_ids']:
            bill = AccountMove.create(bill_vals)
            
            # Link each repack order to its corresponding bill line
            line_index = 0
            for repack in done_repacks:
                if repack.qty_supplied > 0:
                    bill_line = bill.invoice_line_ids[line_index]
                    repack.write({
                        'bill_id': bill.id,
                        'bill_line_id': bill_line.id
                    })
                    line_index += 1
            
            # For repack orders with zero quantity, only link the bill
            zero_qty_repacks = done_repacks.filtered(lambda r: r.qty_supplied <= 0)
            if zero_qty_repacks:
                zero_qty_repacks.write({'bill_id': bill.id})
            
            # Return action to view the created bill
            return {
                'name': _('Created Bill'),
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': bill.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
        else:
            raise UserError(_("No lines to create in the bill. All selected repack orders have zero quantity."))
        
        return True
    
    def name_get(self):
        res = []
        for record in self:
            name = ''
            if record.sale_line_id.display_name:
                name = record.sale_line_id.display_name + ' - '+record.lot_id.display_name
            res.append((record.id,name))
        return res


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


class RepackCreateWizard(models.TransientModel):
    _name = 'repack.create.wizard'
    _description = 'Create Repack from Sale Order'

    sale_id = fields.Many2one('sale.order', required=True, readonly=True)
    line_ids = fields.One2many('repack.create.wizard.line', 'wizard_id')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        sale = self.env['sale.order'].browse(self.env.context.get('active_id'))
        if not sale:
            raise UserError(_('No active Sale Order.'))
        res['sale_id'] = sale.id
        res['line_ids'] = [(0, 0, {
            'sale_line_id': so_line.id,
            'product_id': so_line.product_id.id,
            'qty': so_line.product_uom_qty,
            'lot_id': so_line.lot_id.id,
            'repack_type': (so_line.repack_type or 'none'),
            'repack_comments': so_line.repack_comments,
        }) for so_line in sale.order_line]
        return res

    def action_create_repack(self):
        self.ensure_one()
        # Asegura que lo editado en el árbol ya esté “bajado”:
        self.flush()
        self.line_ids.flush()

        Repack = self.env['repack.order']
        created = []

        for wl in self.line_ids:
            # Solo crear si se seleccionó un tipo válido
            if wl.repack_type and wl.repack_type != 'none':
                # Fallbacks robustos a la SOL
                product = wl.product_id or wl.sale_line_id.product_id
                qty = wl.qty if wl.qty not in (False, None) else wl.sale_line_id.product_uom_qty
                lot = wl.lot_id  # puede quedar vacío si no manejas lote aquí

                if not product:
                    # Si lo quieres opcional, cambia a "continue"
                    raise UserError(_("Missing product on a wizard line."))

                vals = {
                    'product_id': product.id,
                    'lot_id': lot.id if lot else False,
                    'process_type': wl.repack_type,
                    'qty_to_repack': qty or 0.0,
                    'sale_line_id': wl.sale_line_id.id,
                    'comments': wl.repack_comments,
                    'creation_date': fields.Datetime.now(),
                }
                rep = Repack.create(vals)
                created.append(rep.id)

                # Sincroniza con la línea de venta
                wl.sale_line_id.sudo().write({
                    'repack_processed': True,
                    'repack_status': 'process',
                    'repack_type': wl.repack_type,
                    'repack_comments': wl.repack_comments,
                })

        if not created:
            return {'type': 'ir.actions.act_window_close'}

        action = self.env.ref('yrepack_management.action_repack_order', raise_if_not_found=False)
        if action:
            act = action.read()[0]
            act['domain'] = [('id', 'in', created)]
            return act
        return {'type': 'ir.actions.act_window_close'}


class RepackCreateWizardLine(models.TransientModel):
    _name = 'repack.create.wizard.line'
    _description = 'Create Repack Wizard Line'

    wizard_id = fields.Many2one('repack.create.wizard', required=True, ondelete='cascade')
    sale_line_id = fields.Many2one('sale.order.line', string='Sales Line', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    lot_id = fields.Many2one(
        'stock.production.lot', string='Lot',
        domain="[('product_id', '=', product_id)]"
    )
    qty = fields.Float(string='Qty')  # (puedes añadir precision si quieres)
    repack_type = fields.Selection([
        ('none', 'No Repack'),
        ('repack', 'Repack'),
        ('peeled', 'Peeled'),
        ('untailed', 'Untailed'),
        ('rot', 'Remove rot'),
    ], string='Repack Type', default='none')
    repack_comments = fields.Text(string='Comments')