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
            'comments' : 'Created with Python and XlsxWrite from Odoo 13.0'
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
            'font_color' : 'red',
            'font_size'  : '10', 
            'font_name'  : 'arial',
            'border'     : 2,
            'bg_color'   : 'yellow',
            'bold'       : True,
            'align'      : 'center', 
        })
        report_format_title = workbook.add_format({
            'font_color' : 'red',
            'font_size'  : '16',
            'font_name'  : 'arial', 
            'border'     : 2,
            'bg_color'   : 'yellow',
            'bold'       : True,
            'align'      : 'center', 
        })
        bold_header = workbook.add_format({
            'font_color' : 'red',
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 2,
            'bg_color'   : 'yellow',
            'bold'       : True,
            'align'      : 'center',
        })
        light_header_top = workbook.add_format({
            'font_color' : 'red',
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'top'        : 2,
            'right'      : 1,
            'left'       : 1,
            'bottom'     : 1,
            'bg_color'   : 'yellow',
            'align'      : 'center',
        })
        light_header_bottom = workbook.add_format({
            'font_color' : 'red',
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 2,
            'top'        : 1, 
            'right'      : 1,
            'left'       : 1,
            'bg_color'   : 'yellow',
            'align'      : 'center',
        })
        light_box = workbook.add_format({
            'font_color' : 'red',
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 1,
            'top'        : 1, 
            'right'      : 1,
            'left'       : 1,
            'bg_color'   : 'yellow',
            'align'      : 'center',
        })
        light_box_currency = workbook.add_format({
            'font_color' : 'red',
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 1,
            'top'        : 1, 
            'right'      : 1,
            'left'       : 1,
            'bg_color'   : 'yellow',
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
        datestring = fields.Date.from_string(str(data.get('date'),)).strftime(lang_id.date_format)
        
        i = 9
        
        sheet.write(4, 0, 'NOTA', report_format)
        sheet.write(4, 1, 'VIAJE', report_format)
        
        sheet.write(5, 0, '', report_format)
        sheet.write(5, 1, '', report_format)
        
        sheet.write(6, 0, '', report_format)
        sheet.write(6, 1, '', report_format)
        sheet.write(6, 2, '', light_header_top)
        sheet.write(6, 3, 'Cajas', light_header_top)
        sheet.write(6, 4, 'Cajas', light_header_top)
        sheet.write(6, 5, '$', light_header_top)
        sheet.write(6, 6, '$', light_header_top)
        sheet.write(6, 7, '(-)Flete', light_header_top)
        sheet.write(6, 8, '', light_header_top)
        sheet.write(6, 9, 'Precio Compra', light_header_top)
        sheet.write(6, 10, '', light_header_top)
        
        sheet.write(7, 0, 'Fecha', bold_header)
        sheet.write(7, 1, 'Producto', light_header_bottom)
        sheet.write(7, 2, 'Medida', light_header_bottom)
        sheet.write(7, 3, 'Emb.', light_header_bottom)
        sheet.write(7, 4, 'Rec.', light_header_bottom)
        sheet.write(7, 5, 'P.Unit.', light_header_bottom)
        sheet.write(7, 6, 'Importe.', light_header_bottom)
        sheet.write(7, 7, '', light_header_bottom)
        sheet.write(7, 8, '', light_header_bottom)
        sheet.write(7, 9, '', light_header_bottom)
        sheet.write(7, 10, 'total', bold_header)
        
        sheet.write(9, 0, datestring, light_box)
        sheet.write(9, 10, data.get('freight_spoilage_total'), light_box_currency)
        for line in data.get('lines'):
            i += 1
            sheet.write(i, 0, '', light_box)
            sheet.write(i, 1, line.get('product'), light_box)
            sheet.write(i, 2, line.get('product_uom'), light_box)
            sheet.write(i, 3, line.get('box_emb'), light_box)
            sheet.write(i, 4, line.get('box_rec'), light_box)
            sheet.write(i, 5, line.get('price_unit'), light_box_currency)
            sheet.write(i, 6, line.get('amount'), light_box_currency)
            sheet.write(i, 7, line.get('freight'), light_box_currency)
            sheet.write(i, 8, line.get('spoilage'), light_box_currency)
            sheet.write(i, 9, line.get('stock_value'), light_box_currency)
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
        sheet.write(19, 3, data.get('box_emb_total'), light_box)
        sheet.write(19, 4, data.get('box_rec_total'), light_box)
        sheet.write(19, 5, '', light_box)
        sheet.write(19, 6, data.get('amount_total'), light_box_currency)
        sheet.write(19, 7, data.get('freight_total'), light_box_currency)
        sheet.write(19, 8, data.get('spoilage_total'), light_box_currency)
        sheet.write(19, 9, '', light_box)
        sheet.write(19, 10, data.get('total'), light_box_currency)


        sheet.merge_range(5, 2, 5, 10, data.get('company'), report_format_title)
        
        
        sheet.write(4, 17, 'Viaje', travels)
        sheet.write(5, 17, 'VENTAS', travels_title_top_left)
        sheet.write(8, 17, 'LIQUIDACIONES', travels_middle_left)
        sheet.write(9, 17, 'Freight In', travels_middle_left)
        sheet.write(10, 17, 'Aduana', travels_middle_left)
        sheet.write(11, 17, 'MANIOBRAS', travels_middle_left_red)
        sheet.write(12, 17, 'AJUSTE', travels_middle_left_red)
        sheet.write(13, 17, 'STORAGE', travels_middle_left_red)
        sheet.write(14, 17, 'FREIGHT OUT', travels_middle_left_red)
        sheet.write(17, 17, 'UTILIDAD', travels_middle_left)
        sheet.write(5, 18, data.get('sales'), travels_title_top_right)
        sheet.write(9, 18, data.get('freight_in'), travels_middle_right)
        sheet.write(10, 18, data.get('aduana'), travels_middle_right)
        sheet.write(11, 18, data.get('maneuvers'), travels_middle_right_red)
        sheet.write(12, 18, data.get('adjustment'), travels_middle_right_red)
        sheet.write(13, 18, data.get('storage'), travels_middle_right_red)
        sheet.write(14, 18, data.get('freight_out'), travels_middle_right_red)
        sheet.write(17, 18, data.get('utility'), travels_middle_right)
        sheet.write(19, 18, str(data.get('utility_percentage')) + '%', travels_bottom_right)

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
        sheet.write(6, 17, '', travels_middle_left)
        sheet.write(7, 17, '', travels_middle_left)
        sheet.write(15, 17, '', travels_middle_left)
        sheet.write(16, 17, '', travels_middle_left)
        sheet.write(18, 17, '', travels_middle_left)
        sheet.write(6, 18, '', travels_middle_right)
        sheet.write(7, 18, '', travels_middle_right)
        sheet.write(8, 18, '', travels_middle_right)
        sheet.write(15, 18, '', travels_middle_right)
        sheet.write(16, 18, '', travels_middle_right)
        sheet.write(18, 18, '', travels_middle_right)
        sheet.write(19, 17, '', travels_bottom_left)
        
        
    