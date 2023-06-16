# -*- encoding: utf-8 -*-

import time
from odoo import models, api, _, fields
from odoo.exceptions import UserError
from odoo.tools import float_repr, float_round
from datetime import datetime

import logging 
_logger = logging.getLogger(__name__)


class XlsxReport(models.AbstractModel): 
    _name = 'report.liquidaciones.xlsx_report'
    _inherit = 'report.odoo_report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties({
            'comments': 'Created with Python and XlsxWrite from Odoo 13.0'
        })
        sheet = workbook.add_worksheet(_('Plantilla'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(100)
        sheet.set_column(4, 0, 25)
        sheet.set_column(4, 1, 25)
        sheet.set_column(8, 9, 20)
        sheet.set_column(4, 17, 30)
        sheet.set_column(4, 18, 20)
        
        report_format = workbook.add_format({
            'font_size'  : '10',
            'font_name'  : 'arial',
            'border'     : 2,
            'bold'       : True,
            'align'      : 'center',
        })
        report_format_gray = workbook.add_format({
            'font_size'  : '10',
            'font_name'  : 'arial',
            'border'     : 2,
            'bold'       : True,
            'align'      : 'center',
            'bg_color'   : 'gray',
        })
        report_format_title = workbook.add_format({
            'font_color' : 'white',
            'font_size'  : '16',
            'font_name'  : 'arial',
            'border'     : 2,
            'bg_color'   : 'green',
            'bold'       : True,
            'align'      : 'center',
        })
        bold_header = workbook.add_format({
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 2,
            'bold'       : True,
            'align'      : 'center',
        })
        light_header_top = workbook.add_format({
            'font_size'  : '14',
            'font_name'  : 'arial',
            'top'        : 2,
            'right'      : 1,
            'left'       : 1,
            'bottom'     : 1,
            'align'      : 'center',
        })
        light_header_bottom = workbook.add_format({
            'font_size'  : '14',
            'font_name'  : 'arial',
            'bottom'     : 2,
            'top'        : 1,
            'right'      : 1,
            'left'       : 1,
            'align'      : 'center',
        })
        light_box = workbook.add_format({
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 1,
            'top'        : 1, 
            'right'      : 1,
            'left'       : 1,
            'align'      : 'center',
        })
        light_box_currency = workbook.add_format({
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 1,
            'top'        : 1, 
            'right'      : 1,
            'left'       : 1,
            'align'      : 'center',
        })
        travels = workbook.add_format({
            'font_color' : 'black',
            'font_size'  : '14',  
            'font_name'  : 'arial',
            'align'      : 'left',
            'bold'       : True
        })
        travels_title_top_left = workbook.add_format({
            'font_color' : 'black', 
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'left', 
            'top'        : 2, 
            'left'       : 2,
            'bold'       : True
        })
        travels_middle_left = workbook.add_format({
            'font_color' : 'black',
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'left', 
            'left'       : 2,
            'bold'       : True
        })
        travels_bottom_left = workbook.add_format({
            'font_color' : 'black',
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'left', 
            'left'       : 2,
            'bottom'     : 2,
            'bold'       : True
        })
        travels_middle_left_red = workbook.add_format({
            'font_color' : 'white',
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'left', 
            'left'       : 2, 
            'bg_color'   : 'red',
            'bold'       : True
        })
        travels_title_top_right = workbook.add_format({
            'font_color' : 'black', 
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'right', 
            'top'        : 2, 
            'right'      : 2,
            'bold'       : True
        })
        travels_middle_right = workbook.add_format({
            'font_color' : 'black',
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'right', 
            'right'      : 2,
            'bold'       : True
        })
        travels_middle_right_red = workbook.add_format({
            'font_color' : 'white',
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'right', 
            'right'      : 2, 
            'bg_color'   : 'red',
            'bold'       : True
        })
        travels_bottom_right = workbook.add_format({
            'font_color' : 'black',
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'right', 
            'right'      : 2,
            'bottom'     : 2,
            'bold'       : True
        })
        currency_id = self.env.user.company_id.currency_id
        light_box_currency.num_format = currency_id.symbol + '#,##0.00'
        lang = self.env.user.lang
        lang_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        datestring = data.get('date') and fields.Date.from_string(str(data.get('date'),)).strftime(lang_id.date_format)
        i = 9
        sheet.write(4, 0, 'NOTA', report_format_gray)
        sheet.write(4, 1, 'VIAJE', report_format_gray)
        
        sheet.write(5, 0, data.get("note"), report_format_title)
        sheet.write(5, 1, data.get("viaje"), report_format_title)
        
        sheet.write(6, 0, '', report_format)
        sheet.write(6, 1, '', report_format)
        sheet.write(6, 2, '', light_header_top)
        # sheet.write(6, 3, 'Cajas', light_header_top)
        sheet.write(6, 3, 'Cajas', light_header_top)
        sheet.write(6, 4, '$', light_header_top)
        sheet.write(6, 5, '$', light_header_top)
        sheet.write(6, 6, '(-)Flete', light_header_top)
        sheet.write(6, 7, 'Aduana', light_header_top)
        sheet.write(6, 8, 'In&Out', light_header_top)
        sheet.write(6, 9, '(-)Comision', light_header_top)
        sheet.write(6, 10, '', light_header_top)
        
        sheet.write(7, 0, 'Fecha', bold_header)
        sheet.write(7, 1, 'Producto', light_header_bottom)
        sheet.write(7, 2, 'Medida', light_header_bottom)
        # sheet.write(7, 3, 'Emb.', light_header_bottom)
        sheet.write(7, 3, 'Rec.', light_header_bottom)
        sheet.write(7, 4, 'P.Unit.', light_header_bottom)
        sheet.write(7, 5, 'Importe.', light_header_bottom)
        sheet.write(7, 6, '', light_header_bottom)
        sheet.write(7, 7, '', light_header_bottom)
        sheet.write(7, 8, '', light_header_bottom)
        sheet.write(
            7, 9,
            "%d %%" % data.get("commission_percentage", 0.0),
            light_header_bottom)
        sheet.write(7, 10, 'Total', light_header_bottom)

        sheet.write(9, 0, datestring, light_box)
        for line in data.get('lines', []):
            i += 1
            sheet.write(i, 0, '', light_box)
            sheet.write(i, 1, line.get('product', ''), light_box)
            sheet.write(i, 2, line.get('product_uom', ''), light_box)
            sheet.write(i, 3, line.get('box_rec', 0), light_box)
            sheet.write(i, 4, line.get('price_unit', 0.0), light_box_currency)
            sheet.write(i, 5, line.get('amount', 0.0), light_box_currency)
            sheet.write(i, 6, "", light_box_currency)
            sheet.write(i, 7, "", light_box_currency)
            sheet.write(i, 8, "", light_box_currency)
            sheet.write(i, 9, line.get('spoilage'), light_box_currency)
            sheet.write(i, 10, line.get('total'), light_box_currency)
    
        for j in range(19 - i):
            if i < 19:
                i += 1
                sheet.write(i, 0, '', light_box)
                sheet.write(i, 1, '', light_box)
                sheet.write(i, 2, '', light_box)
                sheet.write(i, 3, '', light_box)
                sheet.write(i, 4, '', light_box)
                sheet.write(i, 5, '', light_box)
                sheet.write(i, 6, '', light_box)
                sheet.write(i, 7, '', light_box)
                sheet.write(i, 8, '', light_box)
                sheet.write(i, 9, '', light_box)
                sheet.write(i, 10, '', light_box)
                
        sheet.write(19, 0, '', light_box)
        sheet.write(19, 1, '', light_box)
        sheet.write(19, 2, '', light_box)
        sheet.write(19, 3, data.get('box_rec_total'), light_box)
        sheet.write(19, 4, '', light_box)
        sheet.write(19, 5, data.get('amount_total'), light_box_currency)
        sheet.write(19, 6, data.get('freight_in'), light_box_currency)
        sheet.write(19, 7, data.get('aduana'), light_box_currency)
        sheet.write(19, 8, "", light_box_currency)
        sheet.write(19, 9, data.get('commission_total'), light_box_currency)
        sheet.write(19, 10, data.get('total'), light_box_currency)


        sheet.merge_range(5, 2, 5, 10, data.get('company'), report_format_title)
        
        
        sheet.write(4, 12, 'Viaje', travels)
        sheet.write(5, 12, 'VENTAS', travels_title_top_left)
        sheet.write(8, 12, 'LIQUIDACIONES', travels_middle_left)
        sheet.write(9, 12, 'Freight In', travels_middle_left)
        sheet.write(10, 12, 'Aduana', travels_middle_left)
        sheet.write(11, 12, 'MANIOBRAS', travels_middle_left_red)
        sheet.write(12, 12, 'AJUSTE', travels_middle_left_red)
        sheet.write(13, 12, 'STORAGE', travels_middle_left_red)
        sheet.write(14, 12, 'FREIGHT OUT', travels_middle_left_red)
        sheet.write(17, 12, 'UTILIDAD', travels_middle_left)
        sheet.write(5, 13, data.get('sales'), travels_title_top_right)
        sheet.write(9, 13, data.get('freight_in'), travels_middle_right)
        sheet.write(10, 13, data.get('aduana'), travels_middle_right)
        sheet.write(11, 13, data.get('maneuvers'), travels_middle_right_red)
        sheet.write(12, 13, data.get('adjustment'), travels_middle_right_red)
        sheet.write(13, 13, data.get('storage'), travels_middle_right_red)
        sheet.write(14, 13, data.get('freight_out'), travels_middle_right_red)
        sheet.write(17, 13, data.get('utility'), travels_middle_right)
        sheet.write(19, 13, str(data.get('utility_percentage')) + '%', travels_bottom_right)

        sheet.write(8, 0, '', light_box)
        sheet.write(8, 1, '', light_box)
        sheet.write(8, 2, '', light_box)
        sheet.write(8, 3, '', light_box)
        sheet.write(8, 4, '', light_box)
        sheet.write(8, 5, '', light_box)
        sheet.write(8, 6, '', light_box)
        sheet.write(8, 7, '', light_box)
        sheet.write(8, 8, '', light_box)
        sheet.write(8, 9, '', light_box)
        sheet.write(8, 10, '', light_box)
        sheet.write(9, 1, '', light_box)
        sheet.write(9, 2, '', light_box)
        sheet.write(9, 3, '', light_box)
        sheet.write(9, 4, '', light_box)
        sheet.write(9, 5, '', light_box)
        sheet.write(9, 6, '', light_box)
        sheet.write(9, 7, '', light_box)
        sheet.write(9, 8, '', light_box)
        sheet.write(9, 9, '', light_box)
        sheet.write(9, 10, '', light_box)
        sheet.write(6, 12, '', travels_middle_left)
        sheet.write(7, 12, '', travels_middle_left)
        sheet.write(15, 12, '', travels_middle_left)
        sheet.write(16, 12, '', travels_middle_left)
        sheet.write(18, 12, '', travels_middle_left)
        sheet.write(6, 13, '', travels_middle_right)
        sheet.write(7, 13, '', travels_middle_right)
        sheet.write(8, 13, '', travels_middle_right)
        sheet.write(15, 13, '', travels_middle_right)
        sheet.write(16, 13, '', travels_middle_right)
        sheet.write(18, 13, '', travels_middle_right)
        sheet.write(19, 12, '', travels_bottom_left)


class XlsxUtilityReport(models.AbstractModel): 
    _name = 'report.liquidaciones.xlsx_utility_report'
    _inherit = 'report.odoo_report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties({
            'comments': 'Created with Python and XlsxWrite from Odoo 13.0'
        })
        sheet = workbook.add_worksheet(_('Plantilla'))
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(100)
        sheet.set_column(4, 0, 25)
        sheet.set_column(4, 1, 25)
        sheet.set_column(8, 9, 20)
        sheet.set_column(4, 17, 30)
        sheet.set_column(4, 18, 20)

        travels = workbook.add_format({
            'font_color' : 'black',
            'font_size'  : '14',  
            'font_name'  : 'arial',
            'align'      : 'left',
            'bold'       : True
        })
        name = workbook.add_format({
            'font_color' : 'black',
            'font_size'  : '14',  
            'font_name'  : 'arial',
            'align'      : 'right',
            'bold'       : True
        })
        travels_title_top_left = workbook.add_format({
            'font_color' : 'black', 
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'left', 
            'top'        : 2, 
            'left'       : 2,
            'bold'       : True
        })
        travels_middle_left = workbook.add_format({
            'font_color' : 'black',
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'left', 
            'left'       : 2,
            'bold'       : True
        })
        travels_bottom_left = workbook.add_format({
            'font_color' : 'black',
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'left', 
            'left'       : 2,
            'bottom'     : 2,
            'bold'       : True
        })
        travels_middle_left_red = workbook.add_format({
            'font_color' : 'white',
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'left', 
            'left'       : 2, 
            'bg_color'   : 'red',
            'bold'       : True
        })
        travels_title_top_right = workbook.add_format({
            'font_color' : 'black', 
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'right', 
            'top'        : 2, 
            'right'      : 2,
            'bold'       : True,
            'num_format': '#,##0.00'
        })
        travels_middle_right = workbook.add_format({
            'font_color' : 'black',
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'right', 
            'right'      : 2,
            'bold'       : True,
            'num_format': '#,##0.00'
        })
        travels_middle_right_red = workbook.add_format({
            'font_color' : 'white',
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'right', 
            'right'      : 2, 
            'bg_color'   : 'red',
            'bold'       : True,
            'num_format': '#,##0.00'
        })
        travels_bottom_right = workbook.add_format({
            'font_color' : 'black',
            'font_size'  : '14', 
            'font_name'  : 'arial', 
            'align'      : 'right', 
            'right'      : 2,
            'bottom'     : 2,
            'bold'       : True,
            'num_format': '#,##0.00'
        })
        report_format = workbook.add_format({
            'font_size'  : '10',
            'font_name'  : 'arial',
            'border'     : 2,
            'bold'       : True,
            'align'      : 'center',
        })
        light_header_top = workbook.add_format({
            'font_size'  : '14',
            'font_name'  : 'arial',
            'top'        : 2,
            'right'      : 1,
            'left'       : 1,
            'bottom'     : 1,
            'align'      : 'center',
        })
        light_header_bottom = workbook.add_format({
            'font_size'  : '14',
            'font_name'  : 'arial',
            'bottom'     : 2,
            'top'        : 1,
            'right'      : 1,
            'left'       : 1,
            'align'      : 'center',
        })
        bold_header = workbook.add_format({
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 2,
            'bold'       : True,
            'align'      : 'center',
        })
        light_box = workbook.add_format({
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 1,
            'top'        : 1, 
            'right'      : 1,
            'left'       : 1,
            'align'      : 'center',
        })
        light_box_currency = workbook.add_format({
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 1,
            'top'        : 1, 
            'right'      : 1,
            'left'       : 1,
            'align'      : 'center',
        })
        report_format_gray = workbook.add_format({
            'font_size'  : '10',
            'font_name'  : 'arial',
            'border'     : 2,
            'bold'       : True,
            'align'      : 'center',
            'bg_color'   : 'gray',
        })
        currency_id = self.env.user.company_id.currency_id
        light_box_currency.num_format = currency_id.symbol + '#,##0.00'
        i = 4
        total_total = 0
        total_freight_in = 0
        total_aduana_total = 0
        total_maneuvers_total = 0
        total_adjustment = 0
        total_storage = 0
        total_freight_out = 0
        total_utility = 0
        total_utility_percentage = 0
        utility_per_qty = 0

        for po in objects:
            exists_st = self.env['sale.settlements'].search([('order_id', '=', po.id)], limit=1)
            if exists_st:
                settlement_id = exists_st
                lang = self.env.user.lang
                lang_id = self.env['res.lang'].search([('code', '=', lang)])
                datestring = fields.Date.from_string(str(po.date_order)).strftime(lang_id.date_format)
                sheet.write(i, 0, 'NOTA', report_format_gray)
                sheet.write(i, 1, 'VIAJE', report_format_gray)
                
                sheet.write(i+1, 0, settlement_id.note, report_format_gray)
                sheet.write(i+1, 1, settlement_id.journey, report_format_gray)

                sheet.write(i+2, 0, '', report_format)
                sheet.write(i+2, 1, '', report_format)
                sheet.write(i+2, 2, '', light_header_top)
                # sheet.write(6, 3, 'Cajas', light_header_top)
                sheet.write(i+2, 3, 'Cajas', light_header_top)
                sheet.write(i+2, 4, '$', light_header_top)
                sheet.write(i+2, 5, '$', light_header_top)
                sheet.write(i+2, 6, '(-)Flete', light_header_top)
                sheet.write(i+2, 7, 'Aduana', light_header_top)
                sheet.write(i+2, 8, 'In&Out', light_header_top)
                sheet.write(i+2, 9, '(-)Comision', light_header_top)
                sheet.write(i+2, 10, '', light_header_top)
                
                sheet.write(i+3, 0, 'Fecha', bold_header)
                sheet.write(i+3, 1, 'Producto', light_header_bottom)
                sheet.write(i+3, 2, 'Medida', light_header_bottom)
                # sheet.write(7, 3, 'Emb.', light_header_bottom)
                sheet.write(i+3, 3, 'Rec.', light_header_bottom)
                sheet.write(i+3, 4, 'P.Unit.', light_header_bottom)
                sheet.write(i+3, 5, 'Importe.', light_header_bottom)
                sheet.write(i+3, 6, '', light_header_bottom)
                sheet.write(i+3, 7, '', light_header_bottom)
                sheet.write(i+3, 8, '', light_header_bottom)
                sheet.write(
                    i+3, 9,
                    "%d %%" % settlement_id.commission_percentage,
                    light_header_bottom)
                sheet.write(i+3, 10, 'Total', light_header_bottom)

                sheet.write(i+5, 0, datestring, light_box)
                
                sheet.write(i, 12, 'Viaje', travels)
                sheet.write(i + 1, 12, 'VENTAS', travels_title_top_left)
                sheet.write(i + 4, 12, 'LIQUIDACIONES', travels_middle_left)
                sheet.write(i + 5, 12, 'Freight In', travels_middle_left)
                sheet.write(i + 6, 12, 'Aduana', travels_middle_left)
                sheet.write(i + 7, 12, 'MANIOBRAS', travels_middle_left_red)
                sheet.write(i + 8, 12, 'AJUSTE', travels_middle_left_red)
                sheet.write(i + 9, 12, 'STORAGE', travels_middle_left_red)
                sheet.write(i + 10, 12, 'FREIGHT OUT', travels_middle_left_red)
                sheet.write(i + 13, 12, 'UTILIDAD', travels_middle_left)
                sheet.write(i, 13, po.name, name)
                sheet.write(i + 1, 13, settlement_id.total, travels_title_top_right)
                sheet.write(i + 5, 13, settlement_id.freight_in, travels_middle_right)
                sheet.write(i + 6, 13, settlement_id.aduana_total, travels_middle_right)
                sheet.write(i + 7, 13, settlement_id.maneuvers_total, travels_middle_right_red)
                sheet.write(i + 8, 13, settlement_id.adjustment, travels_middle_right_red)
                sheet.write(i + 9, 13, settlement_id.storage, travels_middle_right_red)
                sheet.write(i + 10, 13, settlement_id.freight_out, travels_middle_right_red)
                sheet.write(i + 13, 13, settlement_id.utility, travels_middle_right)
                sheet.write(i + 15, 13, str(float_round(settlement_id.utility_percentage, precision_digits=2)) + "%", travels_bottom_right)
                sheet.write(i + 2, 12, '', travels_middle_left)
                sheet.write(i + 3, 12, '', travels_middle_left)
                sheet.write(i + 11, 12, '', travels_middle_left)
                sheet.write(i + 12, 12, '', travels_middle_left)
                sheet.write(i + 14, 12, '', travels_middle_left)
                sheet.write(i + 2, 13, '', travels_middle_right)
                sheet.write(i + 3, 13, '', travels_middle_right)
                sheet.write(i + 4, 13, '', travels_middle_right)
                sheet.write(i + 11, 13, '', travels_middle_right)
                sheet.write(i + 12, 13, '', travels_middle_right)
                sheet.write(i + 14, 13, '', travels_middle_right)
                sheet.write(i + 15, 12, '', travels_bottom_left)
                i += 5
                for line in settlement_id.settlements_line_ids:
                    display_name = line.product_id.display_name.replace(
                        ")", "").split("(")
                    variant = len(display_name) > 1 and display_name[1]
                    i += 1
                    sheet.write(i, 0, '', light_box)
                    sheet.write(i, 1, line.product_id.name, light_box)
                    sheet.write(i, 2, variant, light_box)
                    sheet.write(i, 3, line.box_rec, light_box)
                    sheet.write(i, 4, line.price_unit, light_box_currency)
                    sheet.write(i, 5, line.amount, light_box_currency)
                    sheet.write(i, 6, "", light_box_currency)
                    sheet.write(i, 7, "", light_box_currency)
                    sheet.write(i, 8, "", light_box_currency)
                    sheet.write(i, 9, line.commission, light_box_currency)
                    sheet.write(i, 10, line.total, light_box_currency)
                for j in range(19 - i):
                    if i < 19:
                        i += 1
                        sheet.write(i, 0, '', light_box)
                        sheet.write(i, 1, '', light_box)
                        sheet.write(i, 2, '', light_box)
                        sheet.write(i, 3, '', light_box)
                        sheet.write(i, 4, '', light_box)
                        sheet.write(i, 5, '', light_box)
                        sheet.write(i, 6, '', light_box)
                        sheet.write(i, 7, '', light_box)
                        sheet.write(i, 8, '', light_box)
                        sheet.write(i, 9, '', light_box)
                        sheet.write(i, 10, '', light_box)
                
                sheet.write(i+1, 0, '', light_box)
                sheet.write(i+1, 1, '', light_box)
                sheet.write(i+1, 2, '', light_box)
                sheet.write(i+1, 3, "", light_box)
                sheet.write(i+1, 4, '', light_box)
                sheet.write(i+1, 5, settlement_id.total, light_box_currency)
                sheet.write(i+1, 6, settlement_id.freight_total, light_box_currency)
                sheet.write(i+1, 7, settlement_id.aduana_total, light_box_currency)
                sheet.write(i+1, 8, "", light_box_currency)
                sheet.write(i+1, 9, settlement_id.commission, light_box_currency)
                sheet.write(i+1, 10, settlement_id.total_subtotal, light_box_currency)
                
                i += 7

                total_total += settlement_id.total
                total_freight_in += settlement_id.freight_in
                total_aduana_total += settlement_id.aduana_total
                total_maneuvers_total += settlement_id.maneuvers_total
                total_adjustment += settlement_id.adjustment
                total_storage += settlement_id.storage
                total_freight_out += settlement_id.freight_out
                total_utility += settlement_id.utility
                total_utility_percentage = float_round(settlement_id.utility_percentage, precision_digits=2)
                utility_per_qty += 1
            else:
                sheet.write(i, 12, 'Viaje', travels)
                sheet.write(i, 13, po.name, name)
                sheet.write(i+1, 12, "Sin liquidación", name)
                
                sheet.write(i, 0, '', report_format)
                sheet.write(i, 1, '', report_format)
                sheet.write(i, 2, '', light_header_top)
                # sheet.write(6, 3, 'Cajas', light_header_top)
                sheet.write(i, 3, 'Cajas', light_header_top)
                sheet.write(i, 4, '$', light_header_top)
                sheet.write(i, 5, '$', light_header_top)
                sheet.write(i, 6, '(-)Flete', light_header_top)
                sheet.write(i, 7, 'Aduana', light_header_top)
                sheet.write(i, 8, 'In&Out', light_header_top)
                sheet.write(i, 9, '(-)Comision', light_header_top)
                sheet.write(i, 10, '', light_header_top)
                
                sheet.write(i+1, 0, 'Fecha', bold_header)
                sheet.write(i+1, 1, 'Producto', light_header_bottom)
                sheet.write(i+1, 2, 'Medida', light_header_bottom)
                # sheet.write(7, 3, 'Emb.', light_header_bottom)
                sheet.write(i+1, 3, 'Rec.', light_header_bottom)
                sheet.write(i+1, 4, 'P.Unit.', light_header_bottom)
                sheet.write(i+1, 5, 'Importe.', light_header_bottom)
                sheet.write(i+1, 6, '', light_header_bottom)
                sheet.write(i+1, 7, '', light_header_bottom)
                sheet.write(i+1, 8, '', light_header_bottom)
                sheet.write(i+2, 0, 'Sin liquidación', report_format)
                i += 3
        
        i += 1
        sheet.write(i, 1, 'TOTALES', travels)
        sheet.write(i + 1, 1, 'VENTAS', travels_title_top_left)
        sheet.write(i + 4, 1, 'LIQUIDACIONES', travels_middle_left)
        sheet.write(i + 5, 1, 'Freight In', travels_middle_left)
        sheet.write(i + 6, 1, 'Aduana', travels_middle_left)
        sheet.write(i + 7, 1, 'MANIOBRAS', travels_middle_left_red)
        sheet.write(i + 8, 1, 'AJUSTE', travels_middle_left_red)
        sheet.write(i + 9, 1, 'STORAGE', travels_middle_left_red)
        sheet.write(i + 10, 1, 'FREIGHT OUT', travels_middle_left_red)
        sheet.write(i + 13, 1, 'UTILIDAD', travels_middle_left)
        sheet.write(i + 1, 2, total_total, travels_title_top_right)
        sheet.write(i + 5, 2, total_freight_in, travels_middle_right)
        sheet.write(i + 6, 2, total_aduana_total, travels_middle_right)
        sheet.write(i + 7, 2, total_maneuvers_total, travels_middle_right_red)
        sheet.write(i + 8, 2, total_adjustment, travels_middle_right_red)
        sheet.write(i + 9, 2, total_storage, travels_middle_right_red)
        sheet.write(i + 10, 2, total_freight_out, travels_middle_right_red)
        sheet.write(i + 13, 2, total_utility, travels_middle_right)
        sheet.write(i + 15, 2, str(utility_per_qty and total_utility_percentage/utility_per_qty or 0) + '%', travels_bottom_right)

        sheet.write(i + 2, 1, '', travels_middle_left)
        sheet.write(i + 3, 1, '', travels_middle_left)
        sheet.write(i + 11, 1, '', travels_middle_left)
        sheet.write(i + 12, 1, '', travels_middle_left)
        sheet.write(i + 14, 1, '', travels_middle_left)
        sheet.write(i + 2, 2, '', travels_middle_right)
        sheet.write(i + 3, 2, '', travels_middle_right)
        sheet.write(i + 4, 2, '', travels_middle_right)
        sheet.write(i + 11, 2, '', travels_middle_right)
        sheet.write(i + 12, 2, '', travels_middle_right)
        sheet.write(i + 14, 2, '', travels_middle_right)
        sheet.write(i + 15, 1, '', travels_bottom_left)
