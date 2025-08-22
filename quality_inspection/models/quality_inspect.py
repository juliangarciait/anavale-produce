from odoo import models, fields, api

class QualityInspect(models.Model):
    _name = 'quality.inspect'
    _description = 'Quality Inspection'

    stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking', required=False)
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', required=False)
    repack_order_id = fields.Many2one('repack.order', string='Repack Order', required=False)
    lote = fields.Char(string='Lote')
    total_boxes = fields.Integer(string='Total Boxes')
    boxes_per_pallet = fields.Integer(string='Boxes per Pallet')
    temp_recorder = fields.Boolean(string='Temp Recorder')
    defect_percentage = fields.Float(string='Defect Percentage')
    inspector = fields.Char(string='Inspector')
    notes = fields.Text(string='Notes')
    inspection_document_url = fields.Char(string='Inspection Document URL')
    inspection_document_pdf = fields.Binary(string='Inspection Document PDF')
    inspect_line_ids = fields.One2many('quality.inspect.line', 'inspect_id', string='Inspection Lines')

    product_variant_ids = fields.Many2many(
        'product.product', compute='_compute_product_variant_ids', string='Product Variants in Picking', store=False
    )

    @api.depends('stock_picking_id', 'repack_order_id')
    def _compute_product_variant_ids(self):
        for rec in self:
            if rec.stock_picking_id:
                # Usar move_lines para obtener los productos del picking
                rec.product_variant_ids = rec.stock_picking_id.move_lines.mapped('product_id')
            elif rec.repack_order_id:
                rec.product_variant_ids = rec.repack_order_id.product_id
            else:
                rec.product_variant_ids = False


    def action_open_inspect_line_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inspection Line',
            'res_model': 'quality.inspect.line',
            'view_mode': 'form',
            'view_id': self.env.ref('quality_inspection.view_quality_inspect_line_form').id,
            'target': 'new',
            'context': {
                'default_inspect_id': self.id,
            },
        }


class QualityInspectLine(models.Model):
    _name = 'quality.inspect.line'
    _description = 'Quality Inspection Line'

    inspect_id = fields.Many2one('quality.inspect', string='Inspection', required=True, ondelete='cascade')
    variant_id = fields.Many2one('product.product', string='Variant')
    available_variant_ids = fields.Many2many('product.product', string='Available Variants')
    label = fields.Char(string='Label')
    packaging_id = fields.Many2one('product.packaging', string='Packaging')
    inspected_boxes = fields.One2many('inspected.boxes.line', 'inspect_boxes_line_id', string='Inspected Boxes')
    # weight = fields.Float(string='Weight')
    # pieces_per_box = fields.Integer(string='Pieces per Box')
    # defects = fields.One2many('defect.line', 'inspect_line_id', string='Defect Lines')

    @api.onchange('inspect_id')
    def _onchange_inspect_id(self):
        if self.inspect_id and self.inspect_id.stock_picking_id:
            self.available_variant_ids = [(6, 0, self.inspect_id.stock_picking_id.move_lines.mapped('product_id').ids)]
        else:
            self.available_variant_ids = [(5, 0, 0)]
    
    def action_open_inspected_boxes_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Inspected Box',
            'res_model': 'inspected.boxes.line',
            'view_mode': 'form',
            'view_id': self.env.ref('quality_inspection.view_inspected_boxes_line_popup_form').id,
            'target': 'new',
            'context': {
                'default_inspect_boxes_line_id': self.id,
            },
        }

class InspectBoxesLine(models.Model):
    _name = 'inspected.boxes.line'
    _description = 'Inspected Boxes Line'

    inspect_boxes_line_id = fields.Many2one('quality.inspect.line', string='Inspection Line', required=True, ondelete='cascade')
    weight = fields.Float(string='Weight')
    pieces_per_box = fields.Integer(string='Pieces per Box')
    defects = fields.One2many('defect.line', 'inspect_boxes_line_id', string='Defect Lines')


class DefectLine(models.Model):
    _name = 'defect.line'
    _description = 'Defect Line'

    inspect_boxes_line_id = fields.Many2one('inspected.boxes.line', string='Inspection Boxes Line', required=True, ondelete='cascade')
    defect_id = fields.Many2one('defect', string='Defect', required=True)
    quantity = fields.Integer(string='Quantity')
