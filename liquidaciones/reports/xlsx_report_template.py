# -*- encoding: utf-8 -*-

import time
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError
from xlsxwriter.utility import xl_rowcol_to_cell
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
        settlement_id = objects.settlement_ids[0]
        _logger.info(objects.settlement_ids[0])
        _logger.info('$'*100)
        _logger.info(settlement_id)
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
        
        sheet.write(4, 1, 'Viaje', travels)
        sheet.write(5, 1, 'VENTAS', travels_title_top_left)
        sheet.write(8, 1, 'LIQUIDACIONES', travels_middle_left)
        sheet.write(9, 1, 'Freight In', travels_middle_left)
        sheet.write(10, 1, 'Aduana', travels_middle_left)
        sheet.write(11, 1, 'MANIOBRAS', travels_middle_left_red)
        sheet.write(12, 1, 'AJUSTE', travels_middle_left_red)
        sheet.write(13, 1, 'STORAGE', travels_middle_left_red)
        sheet.write(14, 1, 'FREIGHT OUT', travels_middle_left_red)
        sheet.write(17, 1, 'UTILIDAD', travels_middle_left)
        sheet.write(5, 2, settlement_id.total, travels_title_top_right)
        sheet.write(9, 2, settlement_id.freight_in, travels_middle_right)
        sheet.write(10, 2, settlement_id.aduana_total, travels_middle_right)
        sheet.write(11, 2, settlement_id.maneuvers_total, travels_middle_right_red)
        sheet.write(12, 2, settlement_id.adjustment, travels_middle_right_red)
        sheet.write(13, 2, settlement_id.storage, travels_middle_right_red)
        sheet.write(14, 2, settlement_id.freight_out, travels_middle_right_red)
        sheet.write(17, 2, settlement_id.utility, travels_middle_right)
        sheet.write(19, 2, str(settlement_id.utility_percentage) + '%', travels_bottom_right)
        
        sheet.write(6, 1, '', travels_middle_left)
        sheet.write(7, 1, '', travels_middle_left)
        sheet.write(15, 1, '', travels_middle_left)
        sheet.write(16, 1, '', travels_middle_left)
        sheet.write(18, 1, '', travels_middle_left)
        sheet.write(6, 2, '', travels_middle_right)
        sheet.write(7, 2, '', travels_middle_right)
        sheet.write(8, 2, '', travels_middle_right)
        sheet.write(15, 2, '', travels_middle_right)
        sheet.write(16, 2, '', travels_middle_right)
        sheet.write(18, 2, '', travels_middle_right)
        sheet.write(19, 1, '', travels_bottom_left)
