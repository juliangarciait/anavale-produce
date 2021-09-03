from odoo import api, models, _
from odoo.tools import config
from odoo.tools import format_datetime


rec = 0
def autoIncrement():
    global rec
    pStart = 1
    pInterval = 1
    if rec == 0:
        rec = pStart
    else:
        rec += pInterval
    return rec

class MrpStockReport1(models.TransientModel):
    _inherit = 'stock.traceability.report'

    @api.model
    def _get_partner(self, move_line):
        partner = ''
        partner_id = False
        picking_id = move_line.picking_id or move_line.move_id.picking_id
        if picking_id:
            partner_id = picking_id.partner_id.id
            partner = picking_id.partner_id.name
        return partner

    def _make_dict_move(self, level, parent_id, move_line, unfoldable=False):
        res_model, res_id, ref = self._get_reference(move_line)
        dummy, is_used = self._get_linked_move_lines(move_line)
        data = [{
            'level': level,
            'unfoldable': unfoldable,
            'date': format_datetime(self.env, move_line.move_id.date, tz=False, dt_format=False),
            'parent_id': parent_id,
            'is_used': bool(is_used),
            'usage': self._get_usage(move_line),
            'model_id': move_line.id,
            'model': 'stock.move.line',
            'product_id': move_line.product_id.display_name,
            'product_qty_uom': "%s %s" % (self._quantity_to_str(move_line.product_uom_id, move_line.product_id.uom_id, move_line.qty_done), move_line.product_id.uom_id.name),
            'lot_name': move_line.lot_id.name,
            'lot_id': move_line.lot_id.id,
            'location_source': move_line.location_id.name,
            'location_destination': move_line.location_dest_id.name,
            'reference_id': ref,
            'partner': self._get_partner(move_line),
            'res_id': res_id,
            'res_model': res_model}]
        return data

    @api.model
    def _final_vals_to_lines(self, final_vals, level):
        lines = []
        for data in final_vals:
            lines.append({
                'id': autoIncrement(),
                'model': data['model'],
                'model_id': data['model_id'],
                'parent_id': data['parent_id'],
                'usage': data.get('usage', False),
                'is_used': data.get('is_used', False),
                'lot_name': data.get('lot_name', False),
                'lot_id': data.get('lot_id', False),
                'reference': data.get('reference_id', False),
                'partner': data.get('partner', False),
                'res_id': data.get('res_id', False),
                'res_model': data.get('res_model', False),
                'columns': [data.get('reference_id', False),
                            data.get('product_id', False),
                            data.get('date', False),
                            data.get('lot_name', False),
                            data.get('partner', False),
                            data.get('location_source', False),
                            data.get('location_destination', False),
                            data.get('product_qty_uom', 0)],
                'level': level,
                'unfoldable': data['unfoldable'],
            })
        return lines