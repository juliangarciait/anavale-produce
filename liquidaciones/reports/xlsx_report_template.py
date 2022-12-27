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
        sheet.write(9, 0, '', light_box)
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
        sheet.write(10, 0, '', light_box)
        sheet.write(10, 1, '', light_box)
        sheet.write(10, 2, '', light_box)
        sheet.write(10, 3, '', light_box)
        sheet.write(10, 4, '', light_box)
        sheet.write(10, 5, '', light_box)
        sheet.write(10, 6, '', light_box)
        sheet.write(10, 7, '', light_box)
        sheet.write(10, 8, '', light_box)
        sheet.write(10, 9, '', light_box)
        sheet.write(10, 10, '', light_box)
        sheet.write(10, 12, '', light_box)
        sheet.write(10, 13, '', light_box)
        sheet.write(10, 14, '', light_box)
        sheet.write(11, 0, '', light_box)
        sheet.write(11, 1, '', light_box)
        sheet.write(11, 2, '', light_box)
        sheet.write(11, 3, '', light_box)
        sheet.write(11, 4, '', light_box)
        sheet.write(11, 5, '', light_box)
        sheet.write(11, 6, '', light_box)
        sheet.write(11, 7, '', light_box)
        sheet.write(11, 8, '', light_box)
        sheet.write(11, 9, '', light_box)
        sheet.write(11, 10, '', light_box)
        sheet.write(12, 0, '', light_box)
        sheet.write(12, 1, '', light_box)
        sheet.write(12, 2, '', light_box)
        sheet.write(12, 3, '', light_box)
        sheet.write(12, 4, '', light_box)
        sheet.write(12, 5, '', light_box)
        sheet.write(12, 6, '', light_box)
        sheet.write(12, 7, '', light_box)
        sheet.write(12, 8, '', light_box)
        sheet.write(12, 9, '', light_box)
        sheet.write(12, 10, '', light_box)
        sheet.write(13, 0, '', light_box)
        sheet.write(13, 1, '', light_box)
        sheet.write(13, 2, '', light_box)
        sheet.write(13, 3, '', light_box)
        sheet.write(13, 4, '', light_box)
        sheet.write(13, 5, '', light_box)
        sheet.write(13, 6, '', light_box)
        sheet.write(13, 7, '', light_box)
        sheet.write(13, 8, '', light_box)
        sheet.write(13, 9, '', light_box)
        sheet.write(13, 10, '', light_box)
        sheet.write(14, 0, '', light_box)
        sheet.write(14, 1, '', light_box)
        sheet.write(14, 2, '', light_box)
        sheet.write(14, 3, '', light_box)
        sheet.write(14, 4, '', light_box)
        sheet.write(14, 5, '', light_box)
        sheet.write(14, 6, '', light_box)
        sheet.write(14, 7, '', light_box)
        sheet.write(14, 8, '', light_box)
        sheet.write(14, 9, '', light_box)
        sheet.write(14, 10, '', light_box)
        sheet.write(15, 0, '', light_box)
        sheet.write(15, 1, '', light_box)
        sheet.write(15, 2, '', light_box)
        sheet.write(15, 3, '', light_box)
        sheet.write(15, 4, '', light_box)
        sheet.write(15, 5, '', light_box)
        sheet.write(15, 6, '', light_box)
        sheet.write(15, 7, '', light_box)
        sheet.write(15, 8, '', light_box)
        sheet.write(15, 9, '', light_box)
        sheet.write(15, 10, '', light_box)
        sheet.write(16, 0, '', light_box)
        sheet.write(16, 1, '', light_box)
        sheet.write(16, 2, '', light_box)
        sheet.write(16, 3, '', light_box)
        sheet.write(16, 4, '', light_box)
        sheet.write(16, 5, '', light_box)
        sheet.write(16, 6, '', light_box)
        sheet.write(16, 7, '', light_box)
        sheet.write(16, 8, '', light_box)
        sheet.write(16, 9, '', light_box)
        sheet.write(16, 10, '', light_box)
        sheet.write(17, 0, '', light_box)
        sheet.write(17, 1, '', light_box)
        sheet.write(17, 2, '', light_box)
        sheet.write(17, 3, '', light_box)
        sheet.write(17, 4, '', light_box)
        sheet.write(17, 5, '', light_box)
        sheet.write(17, 6, '', light_box)
        sheet.write(17, 7, '', light_box)
        sheet.write(17, 8, '', light_box)
        sheet.write(17, 9, '', light_box)
        sheet.write(17, 10, '', light_box)
        sheet.write(18, 0, '', light_box)
        sheet.write(18, 1, '', light_box)
        sheet.write(18, 2, '', light_box)
        sheet.write(18, 3, '', light_box)
        sheet.write(18, 4, '', light_box)
        sheet.write(18, 5, '', light_box)
        sheet.write(18, 6, '', light_box)
        sheet.write(18, 7, '', light_box)
        sheet.write(18, 8, '', light_box)
        sheet.write(18, 9, '', light_box)
        sheet.write(18, 10, '', light_box)
        sheet.write(19, 0, '', light_box)
        sheet.write(19, 1, '', light_box)
        sheet.write(19, 2, '', light_box)
        sheet.write(19, 3, '', light_box)
        sheet.write(19, 4, '', light_box)
        sheet.write(19, 5, '', light_box)
        sheet.write(19, 6, '', light_box)
        sheet.write(19, 7, '', light_box)
        sheet.write(19, 8, '', light_box)
        sheet.write(19, 9, '', light_box)
        sheet.write(19, 10, '', light_box)


        sheet.merge_range(5, 2, 5, 10, 'AGROFRESH', report_format_title)
        
        
        sheet.write(4, 17, 'Viaje', travels)
        sheet.write(5, 17, 'VENTAS', travels_title_top_left)
        sheet.write(5, 18, '', travels_title_top_right)
        
        sheet.write(6, 17, '', travels_middle_left)
        sheet.write(7, 17, '', travels_middle_left)
        sheet.write(8, 17, 'LIQUIDACIONES', travels_middle_left)
        sheet.write(9, 17, 'Freight In', travels_middle_left)
        sheet.write(10, 17, 'Aduana', travels_middle_left)
        sheet.write(15, 17, '', travels_middle_left)
        sheet.write(16, 17, '', travels_middle_left)
        sheet.write(17, 17, 'UTILIDAD', travels_middle_left)
        sheet.write(18, 17, '', travels_middle_left)
        
        sheet.write(6, 18, '', travels_middle_right)
        sheet.write(7, 18, '', travels_middle_right)
        sheet.write(8, 18, '', travels_middle_right)
        sheet.write(9, 18, '', travels_middle_right)
        sheet.write(10, 18, '', travels_middle_right)
        sheet.write(15, 18, '', travels_middle_right)
        sheet.write(16, 18, '', travels_middle_right)
        sheet.write(17, 18, '', travels_middle_right)
        sheet.write(18, 18, '', travels_middle_right)
        
        sheet.write(11, 17, 'MANIOBRAS', travels_middle_left_red)
        sheet.write(12, 17, 'AJUSTE', travels_middle_left_red)
        sheet.write(13, 17, 'STORAGE', travels_middle_left_red)
        sheet.write(14, 17, 'FREIGHT OUT', travels_middle_left_red)
        sheet.write(11, 18, '', travels_middle_right_red)
        sheet.write(12, 18, '', travels_middle_right_red)
        sheet.write(13, 18, '', travels_middle_right_red)
        sheet.write(14, 18, '', travels_middle_right_red)
        
        sheet.write(19, 17, '', travels_bottom_left)
        sheet.write(19, 18, '', travels_bottom_right)
        
        
    