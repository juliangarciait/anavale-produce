# -*- encoding: utf-8 -*-

import time
from odoo import models, api, _, fields
from odoo.exceptions import UserError
from odoo.tools import float_repr, float_round
from datetime import datetime
import string

import logging 
_logger = logging.getLogger(__name__)

num2alpha = dict(zip(range(1, 27), string.ascii_lowercase))


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
        light_box_currency1 = workbook.add_format({
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 1,
            'top'        : 1, 
            'right'      : 1,
            'left'       : 1,
            'align'      : 'center',
            'num_format' : '0.00'
        })
        light_box_currency_percent = workbook.add_format({
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 1,
            'top'        : 1, 
            'right'      : 1,
            'left'       : 1,
            'align'      : 'center',
            'num_format' : '0.00%'
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
            sheet.write(i, 5, "=d%d*e%d" % (i+1,i+1),light_box_currency)
            sheet.write(i, 6, "", light_box_currency)
            sheet.write(i, 7, "", light_box_currency)
            sheet.write(i, 8, "", light_box_currency)
            #sheet.write(i, 9, line.get('spoilage'), light_box_currency)
            sheet.write(i, 9, "=f%d*J8" % (i+1),light_box_currency)
            sheet.write(i, 10, "=f%d-j%d" % (i+1,i+1), light_box_currency)
    
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
        #sheet.write(19, 3, data.get('box_rec_total'), light_box)
        sheet.write(19, 3, '=SUM(D9:d19)', light_box)
        sheet.write(19, 4, '', light_box)
        #sheet.write(19, 5, data.get('amount_total'), light_box_currency)
        sheet.write(19, 5, '=SUM(f9:f19)', light_box_currency)
        sheet.write(19, 6, data.get('freight_total'), light_box_currency)
        sheet.write(19, 7, data.get('aduana'), light_box_currency)
        sheet.write(19, 8, data.get('storage')+data.get('maneuvers'), light_box_currency1)   
        #sheet.write(19, 9, data.get('commission_total'), light_box_currency)
        sheet.write(19, 9, '=SUM(j9:j19)', light_box_currency)
        #sheet.write(19, 10, data.get('total'), light_box_currency)
        sheet.write(19, 10, '=SUM(k9:k19)', light_box_currency)
        sheet.write(8, 10, '=-SUM(g20:i20)', light_box_currency)  #suma de gastos en total


        sheet.merge_range(5, 2, 5, 10, data.get('company'), report_format_title)
        
        
        sheet.write(4, 12, 'Viaje', travels)
        sheet.write(5, 12, 'VENTAS', travels_title_top_left)
        sheet.write(6, 12, 'STOCK', travels_title_top_left)
        sheet.write(7, 12, 'POR FACTURAR', travels_title_top_left)
        sheet.write(8, 12, 'LIQUIDACIONES', travels_middle_left)
        sheet.write(9, 12, 'Freight In', travels_middle_left)
        sheet.write(10, 12, 'Aduana', travels_middle_left)
        sheet.write(11, 12, 'MANIOBRAS', travels_middle_left_red)
        sheet.write(12, 12, 'AJUSTE', travels_middle_left_red)
        sheet.write(13, 12, 'STORAGE', travels_middle_left_red)
        sheet.write(14, 12, 'FREIGHT OUT', travels_middle_left_red)
        sheet.write(15, 12, 'CAJAS', travels_middle_left_red)
        sheet.write(17, 12, 'UTILIDAD', travels_middle_left)
        sheet.write(5, 13, data.get('ventas_update'), travels_title_top_right)
        sheet.write(8, 13, '=k20', light_box_currency)
        sheet.write(6, 13, data.get('pending_invoice_value'), travels_middle_right)
        sheet.write(7, 13, data.get('stock_value'), travels_middle_right)
        sheet.write(9, 13, data.get('freight_update'), travels_middle_right)
        sheet.write(10, 13, data.get('aduana_update'), travels_middle_right)
        sheet.write(11, 13, data.get('maneuvers_update'), travels_middle_right_red)
        sheet.write(12, 13, data.get('adjustment_update'), travels_middle_right_red)
        sheet.write(13, 13, data.get('storage_update'), travels_middle_right_red)
        sheet.write(14, 13, data.get('freight_out_update'), travels_middle_right_red)
        sheet.write(14, 13, data.get('boxes_update'), travels_middle_right_red)
        #sheet.write(17, 13, data.get('utility'), travels_middle_right)
        sheet.write(17, 13, '=N6-(SUM(N9:N16))', travels_middle_right)
        #sheet.write(19, 13, str(data.get('utility_percentage')) + '%', travels_bottom_right)
        cell_format1 = workbook.add_format()
        sheet.write(19, 13, '=N18/(N6)', light_box_currency_percent)

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
        #sheet.write(8, 10, '', light_box)
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
        #sheet.write(8, 13, '', travels_middle_right)
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
        sumador = i
        inicio_i = 0
        total_total = 0
        total_freight_in = 0
        total_aduana_total = 0
        total_maneuvers_total = 0
        total_adjustment = 0
        total_storage = 0
        total_freight_out = 0
        total_boxes = 0
        total_utility = 0
        total_utility_percentage = 0
        utility_per_qty = 0

        for po in objects:
            exists_st = self.env['sale.settlements'].search([('order_id', '=', po.id)], limit=1)
            if exists_st:
                #codigo para determinar datos actualizables
                po_product_ids = [line.product_id for line in po.order_line]
                fecha = po.date_order
                picking_ids = po.picking_ids.filtered(lambda picking: picking.state == 'done') # Se obtinenen pickings de la orden de compra
                lot_ids = self.env["stock.production.lot"]
                for sml in picking_ids.move_line_ids:
                    lot_ids += sml.lot_id
                analytic_tag_ids = self.env['account.analytic.tag']
                for lot in lot_ids:
                    tag = lot.analytic_tag_ids.filtered(lambda tag: len(tag.name)>5)
                    if not tag in analytic_tag_ids:
                        analytic_tag_ids += tag
                move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
                sales_lines = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.product_id in po_product_ids and line.move_id.state == 'posted')
                freight_in = move_line_ids.filtered(lambda line: line.account_id.id == 1387 and line.move_id.state == 'posted')
                freight_out = move_line_ids.filtered(lambda line: line.account_id.id == 1394 and line.move_id.state == 'posted')
                maneuvers = move_line_ids.filtered(lambda line: line.account_id.id == 1390 and line.move_id.state == 'posted')
                storage = move_line_ids.filtered(lambda line: line.account_id.id == 1395 and line.move_id.state == 'posted')
                aduana_usa = move_line_ids.filtered(lambda line: line.account_id.id == 1393 and line.move_id.state == 'posted')
                aduana_mex = move_line_ids.filtered(lambda line: line.account_id.id == 1392 and line.move_id.state == 'posted')#[]1392
                adjustment = move_line_ids.filtered(lambda line: line.account_id.id == 1378 and line.move_id.state == 'posted')
                boxes = move_line_ids.filtered(lambda line: line.account_id.id == 1509 and line.move_id.state == 'posted')
                sale_update = sum([sale.price_subtotal for sale in sales_lines])
                freight_in_update = sum([accline.price_subtotal for accline in freight_in])
                freight_out_update = sum([accline.price_subtotal for accline in freight_out])
                maneuvers_update = sum([accline.price_subtotal for accline in maneuvers])
                storage_update = sum([accline.price_subtotal for accline in storage])
                aduana_usa_update = sum([accline.price_subtotal for accline in aduana_usa])
                aduana_mex_update = sum([accline.price_subtotal for accline in aduana_mex])
                boxes_update = sum([accline.debit for accline in boxes])
                adjustment_update = sum([accline.price_subtotal for accline in adjustment])
                #termina datos actualizables
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
                sheet.write(i+2, 9, 'Boxes', light_header_top)
                sheet.write(i+2, 10, '(-)Comision', light_header_top)
                sheet.write(i+2, 11, '', light_header_top)
                
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
                sheet.write(i+3, 9, '', light_header_bottom)
                sheet.write(
                    i+3, 10,
                    "%d %%" % settlement_id.commission_percentage,
                    light_header_bottom)
                sheet.write(i+3, 11, 'Total', light_header_bottom)

                sheet.write(i+5, 0, datestring, light_box)
                
                sheet.write(i, 13, 'Viaje', travels)
                sheet.write(i + 1, 13, 'VENTAS', travels_title_top_left)
                sheet.write(i + 2, 13, 'POR FACTURAR', travels_title_top_left)
                sheet.write(i + 3, 13, 'STOCK', travels_title_top_left)
                sheet.write(i + 4, 13, 'LIQUIDACIONES', travels_middle_left)
                sheet.write(i + 5, 13, 'Freight In', travels_middle_left)
                sheet.write(i + 6, 13, 'Aduana', travels_middle_left)
                sheet.write(i + 7, 13, 'MANIOBRAS', travels_middle_left_red)
                sheet.write(i + 8, 13, 'AJUSTE', travels_middle_left_red)
                sheet.write(i + 9, 13, 'STORAGE', travels_middle_left_red)
                sheet.write(i + 10, 13, 'FREIGHT OUT', travels_middle_left_red)
                sheet.write(i + 11, 13, 'CAJAS', travels_middle_left_red)
                sheet.write(i + 13, 13, 'UTILIDAD', travels_middle_left)
                sheet.write(i, 14, po.name, name)
                sheet.write(i + 1, 14, sale_update, travels_title_top_right)
                sheet.write(i + 2, 14, data.get('pending_invoice_value'), travels_middle_right)
                sheet.write(i + 3, 14, data.get('stock_value'), travels_middle_right)
                sheet.write(i + 5, 14, data.get('freight_update'), travels_middle_right)
                sheet.write(i + 6, 14, data.get('aduana_update'), travels_middle_right)
                sheet.write(i + 7, 14, data.get('maneuvers_update'), travels_middle_right_red)
                sheet.write(i + 8, 14, data.get('adjustment_update'), travels_middle_right_red)
                sheet.write(i + 9, 14, data.get('storage_update'), travels_middle_right_red)
                sheet.write(i + 10, 14, data.get('freight_out_update'), travels_middle_right_red)
                sheet.write(i + 11, 14, data.get('boxes_update'), travels_middle_right_red)
                sheet.write(i + 13, 14, settlement_id.utility, travels_middle_right)
                sheet.write(i + 15, 14, str(float_round(settlement_id.utility_percentage, precision_digits=2)) + "%", travels_bottom_right)
                sheet.write(i + 2, 13, '', travels_middle_left)
                sheet.write(i + 3, 13, '', travels_middle_left)
                #sheet.write(i + 11, 13, '', travels_middle_left)
                sheet.write(i + 12, 13, '', travels_middle_left)
                sheet.write(i + 14, 13, '', travels_middle_left)
                sheet.write(i + 2, 14, '', travels_middle_right)
                sheet.write(i + 3, 14, '', travels_middle_right)
                sheet.write(i + 4, 14, settlement_id.settlement, travels_middle_right)
                #sheet.write(i + 11, 14, '', travels_middle_right)
                sheet.write(i + 12, 14, '', travels_middle_right)
                sheet.write(i + 14, 14, '', travels_middle_right)
                sheet.write(i + 15, 13, '', travels_bottom_left)
                liquidacion_ubicacion = i + 4
                i += 5
                j = i - 1
                inicio_i = i
                final_i = i
                sheet.write(i - 1, 11, (-settlement_id.freight_total-settlement_id.aduana_total-settlement_id.storage-settlement_id.maneuvers-settlement_id.boxes), light_box_currency)
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
                    sheet.write(i, 5, "=d{}*e{}".format(str(i+1), str(i+1)), light_box_currency)
                    sheet.write(i, 6, "", light_box_currency)
                    sheet.write(i, 7, "", light_box_currency)
                    sheet.write(i, 8, "", light_box_currency)
                    sheet.write(i, 9, "", light_box_currency)
                    sheet.write(i, 10, "=f{}*k{}".format(str(i+1), str(j)), light_box_currency)
                    sheet.write(i, 11, "=f{}-k{}".format(str(i+1), str(i+1)), light_box_currency)
                    final_i = i
                for jj in range(9-(final_i - inicio_i)):
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
                    sheet.write(i, 11, '', light_box)
                    sumador = sumador +3
                
                
                sheet.write(i+1, 0, '', light_box)
                sheet.write(i+1, 1, '', light_box)
                sheet.write(i+1, 2, '', light_box)
                sheet.write(i+1, 3, "", light_box)
                sheet.write(i+1, 4, '', light_box)
                sheet.write(i+1, 5, "=sum(f{}:f{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                sheet.write(i+1, 6, settlement_id.freight_total, light_box_currency)
                sheet.write(i+1, 7, settlement_id.aduana_total, light_box_currency)
                sheet.write(i+1, 8, settlement_id.storage + settlement_id.maneuvers , light_box_currency)
                sheet.write(i+1, 9, settlement_id.boxes , light_box_currency)
                sheet.write(i+1, 10, "=sum(k{}:k{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                sheet.write(i+1, 11, "=sum(l{}:l{})".format(str(inicio_i), str(i+1)), light_box_currency)
                sheet.write(liquidacion_ubicacion, 14, "=l{}".format(str(i+2)), travels_middle_right)
                sheet.write(liquidacion_ubicacion+9, 14, "=o{}-sum(o{}:o{})".format(str(liquidacion_ubicacion-2),str(liquidacion_ubicacion),str(liquidacion_ubicacion+9)), travels_middle_right)
                sheet.write(liquidacion_ubicacion+11, 14, "=(o{}/o{})".format(str(liquidacion_ubicacion+10),str(liquidacion_ubicacion-2)), travels_middle_right)
                i += 7

                total_total += settlement_id.total
                total_freight_in += settlement_id.freight_in
                total_aduana_total += settlement_id.aduana_total
                total_maneuvers_total += settlement_id.maneuvers_total
                total_adjustment += settlement_id.adjustment
                total_storage += settlement_id.storage
                total_freight_out += settlement_id.freight_out
                total_utility += settlement_id.utility
                total_boxes += boxes_update
                total_utility_percentage = float_round(settlement_id.utility_percentage, precision_digits=2)
                utility_per_qty += 1
                sumador = sumador + 15
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
                sheet.write(i+1, 9, '', light_header_bottom)
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
        sheet.write(i + 11, 1, 'CAJAS', travels_middle_left)
        sheet.write(i + 1, 2, total_total, travels_title_top_right)
        sheet.write(i + 2, 14, data.get('pending_invoice_value'), travels_middle_right)
        sheet.write(i + 3, 14, data.get('stock_value'), travels_middle_right)
        sheet.write(i + 5, 14, data.get('freight_update'), travels_middle_right)
        sheet.write(i + 6, 14, data.get('aduana_update'), travels_middle_right)
        sheet.write(i + 7, 14, data.get('maneuvers_update'), travels_middle_right_red)
        sheet.write(i + 8, 14, data.get('adjustment_update'), travels_middle_right_red)
        sheet.write(i + 9, 14, data.get('storage_update'), travels_middle_right_red)
        sheet.write(i + 10, 14, data.get('freight_out_update'), travels_middle_right_red)
        sheet.write(i + 11, 14, data.get('boxes_update'), travels_middle_right_red)
        sheet.write(i + 13, 2, total_utility, travels_middle_right)
        sheet.write(i + 15, 2, str(utility_per_qty and total_utility_percentage/utility_per_qty or 0) + '%', travels_bottom_right)

        sheet.write(i + 2, 1, '', travels_middle_left)
        sheet.write(i + 3, 1, '', travels_middle_left)
        #sheet.write(i + 11, 1, '', travels_middle_left)
        sheet.write(i + 12, 1, '', travels_middle_left)
        sheet.write(i + 14, 1, '', travels_middle_left)
        sheet.write(i + 2, 2, '', travels_middle_right)
        sheet.write(i + 3, 2, '', travels_middle_right)
        sheet.write(i + 4, 2, '', travels_middle_right)
        #sheet.write(i + 11, 2, '', travels_middle_right)
        sheet.write(i + 12, 2, '', travels_middle_right)
        sheet.write(i + 14, 2, '', travels_middle_right)
        sheet.write(i + 15, 1, '', travels_bottom_left)

        
class XlsxUtilityReport1(models.AbstractModel): 
    _name = 'report.liquidaciones.xlsx_utility_report1'
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
        sumador = i
        inicio_i = 0
        total_total = 0
        total_freight_in = 0
        total_aduana_total = 0
        total_maneuvers_total = 0
        total_adjustment = 0
        total_storage = 0
        total_freight_out = 0
        total_boxes = 0
        total_utility = 0
        total_utility_percentage = 0
        utility_per_qty = 0

        for po in objects:
            exists_st = self.env['sale.settlements'].search([('id', '=', po.id)], limit=1)
            if exists_st:
                po = exists_st.order_id[0]
                #codigo para determinar datos actualizables
                po_product_ids = [line.product_id for line in po.order_line]
                fecha = po.date_order
                picking_ids = po.picking_ids.filtered(lambda picking: picking.state == 'done') # Se obtinenen pickings de la orden de compra
                lot_ids = self.env["stock.production.lot"]
                for sml in picking_ids.move_line_ids:
                    lot_ids += sml.lot_id
                analytic_tag_ids = self.env['account.analytic.tag']
                for lot in lot_ids:
                    tag = lot.analytic_tag_ids.filtered(lambda tag: len(tag.name)>5)
                    if not tag in analytic_tag_ids:
                        analytic_tag_ids += tag
                move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
                sales_lines = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.product_id in po_product_ids and line.move_id.state == 'posted')
                freight_in = move_line_ids.filtered(lambda line: line.account_id.id == 1387 and line.move_id.state == 'posted')
                freight_out = move_line_ids.filtered(lambda line: line.account_id.id == 1394 and line.move_id.state == 'posted')
                maneuvers = move_line_ids.filtered(lambda line: line.account_id.id == 1390 and line.move_id.state == 'posted')
                storage = move_line_ids.filtered(lambda line: line.account_id.id == 1395 and line.move_id.state == 'posted')
                aduana_usa = move_line_ids.filtered(lambda line: line.account_id.id == 1393 and line.move_id.state == 'posted')
                aduana_mex = move_line_ids.filtered(lambda line: line.account_id.id == 1392 and line.move_id.state == 'posted')#[]1392
                adjustment = move_line_ids.filtered(lambda line: line.account_id.id == 1378 and line.move_id.state == 'posted')
                boxes = move_line_ids.filtered(lambda line: line.account_id.id == 1509 and line.move_id.state == 'posted')
                sale_update = sum([sale.price_subtotal for sale in sales_lines])
                freight_in_update = sum([accline.price_subtotal for accline in freight_in])
                freight_out_update = sum([accline.price_subtotal for accline in freight_out])
                maneuvers_update = sum([accline.price_subtotal for accline in maneuvers])
                storage_update = sum([accline.price_subtotal for accline in storage])
                aduana_usa_update = sum([accline.price_subtotal for accline in aduana_usa])
                aduana_mex_update = sum([accline.price_subtotal for accline in aduana_mex])
                boxes_update = sum([accline.debit for accline in boxes])
                adjustment_update = sum([accline.price_subtotal for accline in adjustment])
                #termina datos actualizables
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
                sheet.write(i+2, 9, 'Boxes', light_header_top)
                sheet.write(i+2, 10, '(-)Comision', light_header_top)
                sheet.write(i+2, 11, '', light_header_top)
                
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
                sheet.write(i+3, 9, '', light_header_bottom)
                sheet.write(
                    i+3, 10,
                    "%d %%" % settlement_id.commission_percentage,
                    light_header_bottom)
                sheet.write(i+3, 11, 'Total', light_header_bottom)

                sheet.write(i+5, 0, datestring, light_box)
                
                sheet.write(i, 13, 'Viaje', travels)
                sheet.write(i + 1, 13, 'VENTAS', travels_title_top_left)
                sheet.write(i + 2, 13, 'POR FACTURAR', travels_title_top_left)
                sheet.write(i + 3, 13, 'STOCK', travels_title_top_left)
                sheet.write(i + 4, 13, 'LIQUIDACIONES', travels_middle_left)
                sheet.write(i + 5, 13, 'Freight In', travels_middle_left)
                sheet.write(i + 6, 13, 'Aduana', travels_middle_left)
                sheet.write(i + 7, 13, 'MANIOBRAS', travels_middle_left_red)
                sheet.write(i + 8, 13, 'AJUSTE', travels_middle_left_red)
                sheet.write(i + 9, 13, 'STORAGE', travels_middle_left_red)
                sheet.write(i + 10, 13, 'FREIGHT OUT', travels_middle_left_red)
                sheet.write(i + 11, 13, 'CAJAS', travels_middle_left_red)
                sheet.write(i + 13, 13, 'UTILIDAD', travels_middle_left)
                sheet.write(i, 14, po.name, name)
                sheet.write(i + 1, 14, sale_update, travels_title_top_right)
                sheet.write(i + 2, 14, data.get('pending_invoice_value'), travels_middle_right)
                sheet.write(i + 3, 14, data.get('stock_value'), travels_middle_right)
                sheet.write(i + 5, 14, data.get('freight_update'), travels_middle_right)
                sheet.write(i + 6, 14, data.get('aduana_update'), travels_middle_right)
                sheet.write(i + 7, 14, data.get('maneuvers_update'), travels_middle_right_red)
                sheet.write(i + 8, 14, data.get('adjustment_update'), travels_middle_right_red)
                sheet.write(i + 9, 14, data.get('storage_update'), travels_middle_right_red)
                sheet.write(i + 10, 14, data.get('freight_out_update'), travels_middle_right_red)
                sheet.write(i + 11, 14, data.get('boxes_update'), travels_middle_right_red)
                sheet.write(i + 13, 14, settlement_id.utility, travels_middle_right)
                sheet.write(i + 15, 14, str(float_round(settlement_id.utility_percentage, precision_digits=2)) + "%", travels_bottom_right)
                #sheet.write(i + 2, 13, '', travels_middle_left)
                #sheet.write(i + 3, 13, '', travels_middle_left)
                #sheet.write(i + 11, 13, '', travels_middle_left)
                sheet.write(i + 12, 13, '', travels_middle_left)
                sheet.write(i + 14, 13, '', travels_middle_left)
                #sheet.write(i + 2, 14, '', travels_middle_right)
                #sheet.write(i + 3, 14, '', travels_middle_right)
                sheet.write(i + 4, 14, settlement_id.settlement, travels_middle_right)
                #sheet.write(i + 11, 14, '', travels_middle_right)
                sheet.write(i + 12, 14, '', travels_middle_right)
                sheet.write(i + 14, 14, '', travels_middle_right)
                sheet.write(i + 15, 13, '', travels_bottom_left)
                liquidacion_ubicacion = i + 4
                i += 5
                j = i - 1
                inicio_i = i
                final_i = i

                costo = 0
                if settlement_id.check_freight_in:
                    costo += settlement_id.freight_in
                if settlement_id.check_freight_out:
                    costo += settlement_id.freight_out
                if settlement_id.check_aduana:
                    costo += settlement_id.aduana
                if settlement_id.check_aduana_mx:
                    costo += settlement_id.aduana_mex
                if settlement_id.check_storage:
                    costo += settlement_id.storage
                if settlement_id.check_adjustment:
                    costo += settlement_id.adjustment 
                if settlement_id.check_maneuvers:
                    costo += settlement_id.maneuvers
                if settlement_id.check_boxes:
                    costo += settlement_id.boxes
                if costo > 0:
                    sheet.write(i - 1, 11, (-costo), light_box_currency)
                else: 
                    sheet.write(i - 1, 11, "", light_box_currency)


                #sheet.write(i - 1, 11, (-settlement_id.freight_total-settlement_id.aduana_total-settlement_id.storage-settlement_id.maneuvers-settlement_id.boxes), light_box_currency)
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
                    sheet.write(i, 5, "=d{}*e{}".format(str(i+1), str(i+1)), light_box_currency)
                    sheet.write(i, 6, "", light_box_currency)
                    sheet.write(i, 7, "", light_box_currency)
                    sheet.write(i, 8, "", light_box_currency)
                    sheet.write(i, 9, "", light_box_currency)
                    sheet.write(i, 10, "=f{}*k{}".format(str(i+1), str(j)), light_box_currency)
                    sheet.write(i, 11, "=f{}-k{}".format(str(i+1), str(i+1)), light_box_currency)
                    final_i = i
                for jj in range(9-(final_i - inicio_i)):
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
                    sheet.write(i, 11, '', light_box)
                    sumador = sumador +3
                
                
                sheet.write(i+1, 0, '', light_box)
                sheet.write(i+1, 1, '', light_box)
                sheet.write(i+1, 2, '', light_box)
                sheet.write(i+1, 3, "", light_box)
                sheet.write(i+1, 4, '', light_box)
                sheet.write(i+1, 5, "=sum(f{}:f{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                suma_freight = 0
                if settlement_id.check_freight_in:
                    suma_freight += settlement_id.freight_in
                if settlement_id.check_freight_out:
                    suma_freight += settlement_id.freight_out
                if suma_freight>0:
                    sheet.write(i+1, 6, suma_freight, light_box_currency)
                else:
                    sheet.write(i+1, 6, "", light_box_currency)

                
                #sheet.write(i+1, 6, settlement_id.freight_total, light_box_currency)

                suma_aduana = 0
                if settlement_id.check_aduana:
                    suma_aduana += settlement_id.aduana
                if settlement_id.check_aduana_mx:
                    suma_aduana += settlement_id.aduana_mex
                if suma_aduana>0:
                    sheet.write(i+1, 7, suma_aduana, light_box_currency)
                else:
                    sheet.write(i+1, 7, "", light_box_currency)
                #sheet.write(i+1, 7, settlement_id.aduana_total, light_box_currency)
                
                
                suma_storage = 0
                if settlement_id.check_maneuvers:
                    suma_storage += settlement_id.maneuvers
                if settlement_id.check_adjustment:
                    suma_storage += settlement_id.adjustment
                if settlement_id.check_storage:
                    suma_storage += settlement_id.storage
                if suma_storage>0:
                    sheet.write(i+1, 8, suma_storage , light_box_currency)
                else:
                    sheet.write(i+1, 8, "" , light_box_currency)
                #sheet.write(i+1, 8, settlement_id.storage + settlement_id.maneuvers , light_box_currency)
                
                if settlement_id.check_boxes:
                    sheet.write(i+1, 9, settlement_id.boxes , light_box_currency)
                else: sheet.write(i+1, 9, "" , light_box_currency)

                #sheet.write(i+1, 9, settlement_id.boxes , light_box_currency)
                sheet.write(i+1, 10, "=sum(k{}:k{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                sheet.write(i+1, 11, "=sum(l{}:l{})".format(str(inicio_i), str(i+1)), light_box_currency)
                sheet.write(liquidacion_ubicacion, 14, "=l{}".format(str(i+2)), travels_middle_right)
                sheet.write(liquidacion_ubicacion+9, 14, "=o{}+o{}+o{}-sum(o{}:o{})".format(str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion),str(liquidacion_ubicacion+1),str(liquidacion_ubicacion+9)), travels_middle_right)
                sheet.write(liquidacion_ubicacion+11, 14, "=(o{}/(o{}+o{}+o{}))".format(str(liquidacion_ubicacion+10),str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion)), travels_middle_right)
                i += 7

                total_total += settlement_id.total
                total_freight_in += settlement_id.freight_in
                total_aduana_total += settlement_id.aduana_total
                total_maneuvers_total += settlement_id.maneuvers_total
                total_adjustment += settlement_id.adjustment
                total_storage += settlement_id.storage
                total_freight_out += settlement_id.freight_out
                total_utility += settlement_id.utility
                total_boxes += boxes_update
                total_utility_percentage = float_round(settlement_id.utility_percentage, precision_digits=2)
                utility_per_qty += 1
                sumador = sumador + 15
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
                sheet.write(i+1, 9, '', light_header_bottom)
                sheet.write(i+2, 0, 'Sin liquidación', report_format)
                i += 3
                

class XlsxUtilityReport_noupdate(models.AbstractModel): 
    _name = 'report.liquidaciones.xlsx_utility_report_noupdate'
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
        sumador = i
        inicio_i = 0
        total_total = 0
        total_freight_in = 0
        total_aduana_total = 0
        total_maneuvers_total = 0
        total_adjustment = 0
        total_storage = 0
        total_freight_out = 0
        total_boxes = 0
        total_utility = 0
        total_utility_percentage = 0
        utility_per_qty = 0

        for po in objects:
            exists_st = self.env['sale.settlements'].search([('id', '=', po.id)], limit=1)
            if exists_st:
                po = exists_st.order_id[0]
                #codigo para determinar datos actualizables
                po_product_ids = [line.product_id for line in po.order_line]
                fecha = po.date_order
                picking_ids = po.picking_ids.filtered(lambda picking: picking.state == 'done') # Se obtinenen pickings de la orden de compra
                lot_ids = self.env["stock.production.lot"]
                for sml in picking_ids.move_line_ids:
                    lot_ids += sml.lot_id
                analytic_tag_ids = self.env['account.analytic.tag']
                for lot in lot_ids:
                    tag = lot.analytic_tag_ids.filtered(lambda tag: len(tag.name)>5)
                    if not tag in analytic_tag_ids:
                        analytic_tag_ids += tag
                move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
                sales_lines = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.product_id in po_product_ids and line.move_id.state == 'posted')
                freight_in = move_line_ids.filtered(lambda line: line.account_id.id == 1387 and line.move_id.state == 'posted')
                freight_out = move_line_ids.filtered(lambda line: line.account_id.id == 1394 and line.move_id.state == 'posted')
                maneuvers = move_line_ids.filtered(lambda line: line.account_id.id == 1390 and line.move_id.state == 'posted')
                storage = move_line_ids.filtered(lambda line: line.account_id.id == 1395 and line.move_id.state == 'posted')
                aduana_usa = move_line_ids.filtered(lambda line: line.account_id.id == 1393 and line.move_id.state == 'posted')
                aduana_mex = move_line_ids.filtered(lambda line: line.account_id.id == 1392 and line.move_id.state == 'posted')#[]1392
                adjustment = move_line_ids.filtered(lambda line: line.account_id.id == 1378 and line.move_id.state == 'posted')
                boxes = move_line_ids.filtered(lambda line: line.account_id.id == 1509 and line.move_id.state == 'posted')


                sale_update = sum([sale.price_subtotal for sale in sales_lines])
                freight_in_update = sum([accline.price_subtotal for accline in freight_in])
                freight_out_update = sum([accline.price_subtotal for accline in freight_out])
                maneuvers_update = sum([accline.price_subtotal for accline in maneuvers])
                storage_update = sum([accline.price_subtotal for accline in storage])
                aduana_usa_update = sum([accline.price_subtotal for accline in aduana_usa])
                aduana_mex_update = sum([accline.price_subtotal for accline in aduana_mex])
                boxes_update = sum([accline.debit for accline in boxes])
                adjustment_update = sum([accline.price_subtotal for accline in adjustment])
                #termina datos actualizables
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
                sheet.write(i+2, 9, 'Boxes', light_header_top)
                sheet.write(i+2, 10, '(-)Comision', light_header_top)
                sheet.write(i+2, 11, '', light_header_top)
                
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
                sheet.write(i+3, 9, '', light_header_bottom)
                sheet.write(
                    i+3, 10,
                    "%d %%" % settlement_id.commission_percentage,
                    light_header_bottom)
                sheet.write(i+3, 11, 'Total', light_header_bottom)

                sheet.write(i+5, 0, datestring, light_box)
                
                liquidacion_ubicacion = i + 4
                i += 5
                j = i - 1
                inicio_i = i
                final_i = i
                #calcular el costo en base a los checkbox
                costo = 0
                if settlement_id.check_freight_in:
                    costo += settlement_id.freight_in
                if settlement_id.check_freight_out:
                    costo += settlement_id.freight_out
                if settlement_id.check_aduana:
                    costo += settlement_id.aduana
                if settlement_id.check_aduana_mx:
                    costo += settlement_id.aduana_mex
                if settlement_id.check_storage:
                    costo += settlement_id.storage
                if settlement_id.check_adjustment:
                    costo += settlement_id.adjustment 
                if settlement_id.check_maneuvers:
                    costo += settlement_id.maneuvers
                if settlement_id.check_boxes:
                    costo += settlement_id.boxes
                if costo > 0:
                    sheet.write(i - 1, 11, (-costo), light_box_currency)
                else: 
                    sheet.write(i - 1, 11, "", light_box_currency)


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
                    sheet.write(i, 5, "=d{}*e{}".format(str(i+1), str(i+1)), light_box_currency)
                    sheet.write(i, 6, "", light_box_currency)
                    sheet.write(i, 7, "", light_box_currency)
                    sheet.write(i, 8, "", light_box_currency)
                    sheet.write(i, 9, "", light_box_currency)
                    sheet.write(i, 10, "=f{}*k{}".format(str(i+1), str(j)), light_box_currency)
                    sheet.write(i, 11, "=f{}-k{}".format(str(i+1), str(i+1)), light_box_currency)
                    final_i = i
                for jj in range(9-(final_i - inicio_i)):
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
                    sheet.write(i, 11, '', light_box)
                    sumador = sumador +3
                
                
                sheet.write(i+1, 0, '', light_box)
                sheet.write(i+1, 1, '', light_box)
                sheet.write(i+1, 2, '', light_box)
                sheet.write(i+1, 3, "", light_box)
                sheet.write(i+1, 4, '', light_box)
                sheet.write(i+1, 5, "=sum(f{}:f{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                suma_freight = 0
                if settlement_id.check_freight_in:
                    suma_freight += settlement_id.freight_in
                if settlement_id.check_freight_out:
                    suma_freight += settlement_id.freight_out
                if suma_freight>0:
                    sheet.write(i+1, 6, suma_freight, light_box_currency)
                else:
                    sheet.write(i+1, 6, "", light_box_currency)

                suma_aduana = 0
                if settlement_id.check_aduana:
                    suma_aduana += settlement_id.aduana
                if settlement_id.check_aduana_mx:
                    suma_aduana += settlement_id.aduana_mex
                if suma_aduana>0:
                    sheet.write(i+1, 7, suma_aduana, light_box_currency)
                else:
                    sheet.write(i+1, 7, "", light_box_currency)
                #sheet.write(i+1, 7, settlement_id.aduana_total, light_box_currency)

                suma_storage = 0
                if settlement_id.check_maneuvers:
                    suma_storage += settlement_id.maneuvers
                if settlement_id.check_adjustment:
                    suma_storage += settlement_id.adjustment
                if settlement_id.check_storage:
                    suma_storage += settlement_id.storage
                if suma_storage>0:
                    sheet.write(i+1, 8, suma_storage , light_box_currency)
                else:
                    sheet.write(i+1, 8, "" , light_box_currency)

                #sheet.write(i+1, 8, settlement_id.storage + settlement_id.maneuvers , light_box_currency)

                if settlement_id.check_boxes:
                    sheet.write(i+1, 9, settlement_id.boxes , light_box_currency)
                else: sheet.write(i+1, 9, "" , light_box_currency)

                
                sheet.write(i+1, 10, "=sum(k{}:k{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                sheet.write(i+1, 11, "=sum(l{}:l{})".format(str(inicio_i), str(i+1)), light_box_currency)
                #sheet.write(liquidacion_ubicacion, 14, "=l{}".format(str(i+2)), travels_middle_right)
                #sheet.write(liquidacion_ubicacion+9, 14, "=o{}-sum(o{}:o{})".format(str(liquidacion_ubicacion-2),str(liquidacion_ubicacion),str(liquidacion_ubicacion+9)), travels_middle_right)
                #sheet.write(liquidacion_ubicacion+11, 14, "=(o{}/o{})".format(str(liquidacion_ubicacion+10),str(liquidacion_ubicacion-2)), travels_middle_right)
                i += 7

                total_total += settlement_id.total
                total_freight_in += settlement_id.freight_in
                total_aduana_total += settlement_id.aduana_total
                total_maneuvers_total += settlement_id.maneuvers_total
                total_adjustment += settlement_id.adjustment
                total_storage += settlement_id.storage
                total_freight_out += settlement_id.freight_out
                total_utility += settlement_id.utility
                total_boxes += boxes_update
                total_utility_percentage = float_round(settlement_id.utility_percentage, precision_digits=2)
                utility_per_qty += 1
                sumador = sumador + 15
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
                sheet.write(i+1, 9, '', light_header_bottom)
                sheet.write(i+2, 0, 'Sin liquidación', report_format)
                i += 3
                
        
class XlsxUtilityReport2(models.AbstractModel): 
    _name = 'report.liquidaciones.xlsx_utility_report2'
    _inherit = 'report.odoo_report_xlsx.abstract'


    def _get_objs_for_report(self, docids, data):
        if docids:
            ids = docids
        elif data and 'context' in data:
            ids = data["context"].get('active_ids', [])
        else:
            ids = self.env.context.get('active_ids', [])
        if docids:
            return self.env['purchase.order'].browse(ids)
        else:
            return self.env['sale.settlements'].browse(ids)

    def generate_xlsx_report(self, workbook, data, objects, sign=True):
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
        light_box_percentage = workbook.add_format({
            'font_color' : 'black',
            'font_size'  : '14', 
            'font_name'  : 'arial',
            'bottom'     : 2, 
            'right'      : 2,
            'align'      : 'right',
            'num_format': '0.00%',
        })
        light_box_percentage.num_format = '0.00%'
        light_box_percentage.set_num_format(10)
        i = 4
        sumador = i
        inicio_i = 0
        total_total = 0
        total_freight_in = 0
        total_aduana_total = 0
        total_maneuvers_total = 0
        total_adjustment = 0
        total_storage = 0
        total_freight_out = 0
        total_boxes = 0
        total_utility = 0
        total_utility_percentage = 0
        total_porfacturar = 0
        total_stock = 0
        utility_per_qty = 0
        liquidaciones = []

        if type(objects) == type(self.env['sale.settlements']):
            procesar_object = objects[0].order_id
        elif type(objects) == type(self.env['purchase.order']):
            procesar_object = objects

        for po in procesar_object:
            exists_st = self.env['sale.settlements'].search([('order_id', '=', po.id)], limit=1)
            if exists_st:
                if exists_st.price_type == 'open':
                    #codigo para determinar datos actualizables
                    po_product_ids = [line.product_id for line in po.order_line]
                    fecha = po.date_order
                    picking_ids = po.picking_ids.filtered(lambda picking: picking.state == 'done') # Se obtinenen pickings de la orden de compra
                    lot_ids = self.env["stock.production.lot"]
                    for sml in picking_ids.move_line_ids:
                        lot_ids += sml.lot_id
                    analytic_tag_ids = self.env['account.analytic.tag']
                    for lot in lot_ids:
                        tag = lot.analytic_tag_ids.filtered(lambda tag: len(tag.name)>5)
                        if not tag in analytic_tag_ids:
                            analytic_tag_ids += tag
                    move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
                    sales_lines = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.move_id.state == 'posted')
                    sales_ajust_lines = move_line_ids.filtered(lambda line: line.account_id.id in (1377, 1379) and line.move_id.state == 'posted')
                    freight_in = move_line_ids.filtered(lambda line: line.account_id.id == 1387 and line.move_id.state == 'posted')
                    freight_out = move_line_ids.filtered(lambda line: line.account_id.id == 1394 and line.move_id.state == 'posted')
                    maneuvers = move_line_ids.filtered(lambda line: line.account_id.id == 1390 and line.move_id.state == 'posted')
                    storage = move_line_ids.filtered(lambda line: line.account_id.id == 1395 and line.move_id.state == 'posted')
                    aduana_usa = move_line_ids.filtered(lambda line: line.account_id.id == 1393 and line.move_id.state == 'posted')
                    aduana_mex = move_line_ids.filtered(lambda line: line.account_id.id == 1392 and line.move_id.state == 'posted')#[]1392
                    adjustment = move_line_ids.filtered(lambda line: line.account_id.id == 1378 and line.move_id.state == 'posted')
                    boxes = move_line_ids.filtered(lambda line: line.account_id.id == 1509 and line.move_id.state == 'posted')
                    logistics = move_line_ids.filtered(lambda line: line.account_id.id == 1516 and line.move_id.state == 'posted')
                    sale_update = sum([sale.price_subtotal for sale in sales_lines])
                    sale_ajust_update = sum([sale.price_subtotal for sale in sales_ajust_lines])
                    sale_update = sale_update - sale_ajust_update
                    freight_in_update = sum([accline.price_subtotal for accline in freight_in])
                    freight_out_update = sum([accline.price_subtotal for accline in freight_out])
                    maneuvers_update = sum([accline.price_subtotal for accline in maneuvers])
                    storage_update = sum([accline.price_subtotal for accline in storage])
                    aduana_usa_update = sum([accline.price_subtotal for accline in aduana_usa])
                    aduana_mex_update = sum([accline.price_subtotal for accline in aduana_mex])
                    boxes_update = sum([accline.debit for accline in boxes])
                    adjustment_update = sum([accline.price_subtotal for accline in adjustment])
                    logistics_update = sum([accline.price_subtotal for accline in logistics])
                    exists_st.calcular_update()

                    #termina datos actualizables

                    #aqui poner el if para open close
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
                    sheet.write(i+2, 9, 'Boxes', light_header_top)
                    sheet.write(i+2, 10, '(-)Comision', light_header_top)
                    sheet.write(i+2, 11, '', light_header_top)
                    
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
                    sheet.write(i+3, 9, '', light_header_bottom)
                    sheet.write(
                        i+3, 10,
                        "%d %%" % settlement_id.commission_percentage,
                        light_header_bottom)
                    sheet.write(i+3, 11, 'Total', light_header_bottom)

                    sheet.write(i+5, 0, datestring, light_box)
                    
                    if len(procesar_object)> 1 or exists_st.actualizacion == True:
                        sheet.write(i, 13, 'Viaje', travels)
                        sheet.write(i + 1, 13, 'VENTAS', travels_title_top_left)
                        sheet.write(i + 2, 13, 'POR FACTURAR', travels_middle_left)
                        sheet.write(i + 3, 13, 'STOCK', travels_middle_left)
                        sheet.write(i + 4, 13, 'LIQUIDACIONES', travels_middle_left)
                        sheet.write(i + 5, 13, 'Freight In', travels_middle_left)
                        sheet.write(i + 6, 13, 'Aduana', travels_middle_left)
                        sheet.write(i + 7, 13, 'MANIOBRAS', travels_middle_left_red)
                        sheet.write(i + 8, 13, 'AJUSTE', travels_middle_left_red)
                        sheet.write(i + 9, 13, 'STORAGE', travels_middle_left_red)
                        sheet.write(i + 10, 13, 'FREIGHT OUT', travels_middle_left_red)
                        sheet.write(i + 11, 13, 'CAJAS', travels_middle_left_red)
                        sheet.write(i + 12, 13, 'LOGISTICS', travels_middle_left_red)
                        sheet.write(i + 13, 13, 'UTILIDAD', travels_middle_left)
                        sheet.write(i, 14, po.name, name)
                        sheet.write(i + 1, 14, sale_update, travels_title_top_right)
                        sheet.write(i + 2, 14, exists_st.pending_invoice_value, travels_middle_right)
                        sheet.write(i + 3, 14, exists_st.stock_value, travels_middle_right)
                        sheet.write(i + 5, 14, freight_in_update, travels_middle_right)
                        sheet.write(i + 6, 14, aduana_usa_update+aduana_mex_update, travels_middle_right)
                        sheet.write(i + 7, 14, maneuvers_update, travels_middle_right_red)
                        sheet.write(i + 8, 14, adjustment_update, travels_middle_right_red)
                        sheet.write(i + 9, 14, storage_update, travels_middle_right_red)
                        sheet.write(i + 10, 14, freight_out_update, travels_middle_right_red)
                        sheet.write(i + 11, 14, boxes_update, travels_middle_right_red)
                        sheet.write(i + 12, 14, logistics_update, travels_middle_right_red)
                        sheet.write(i + 13, 14, settlement_id.utility, travels_middle_right)
                        sheet.write(i + 15, 14, str(float_round(settlement_id.utility_percentage, precision_digits=2)) + "%", travels_bottom_right)
                        #sheet.write(i + 2, 13, '', travels_middle_left)
                        #sheet.write(i + 3, 13, '', travels_middle_left)
                        #sheet.write(i + 11, 13, '', travels_middle_left)
                        #sheet.write(i + 12, 13, '', travels_middle_left)
                        sheet.write(i + 14, 13, '', travels_middle_left)
                        #sheet.write(i + 2, 14, '', travels_middle_right)
                        #sheet.write(i + 3, 14, '', travels_middle_right)
                        sheet.write(i + 4, 14, settlement_id.settlement, travels_middle_right)
                        #sheet.write(i + 11, 14, '', travels_middle_right)
                        #sheet.write(i + 12, 14, '', travels_middle_right)
                        sheet.write(i + 14, 14, '', travels_middle_right)
                        sheet.write(i + 15, 13, '', travels_bottom_left)
                    
                    exists_st.actualizacion = True
                    tabla_ventas_inicial =  i + 5
                    liquidacion_ubicacion = i + 4
                    i += 5
                    j = i - 1
                    inicio_i = i
                    final_i = i
                    sheet.write(i - 1, 11, (-settlement_id.freight_total-settlement_id.aduana_total-settlement_id.storage_total-settlement_id.maneuvers_total-settlement_id.boxes), light_box_currency)
                    loc_total_gastos_row = i -1
                    #activar variables para cuadro vde ventas
                    tb_ventas = []
                    tb_porfacturar = []
                    tb_stock = []
                    tb_scrap = []

                    for line in settlement_id.settlements_line_ids:
                        #tabla de ventas inicio
                        line_lotes =  self.env['stock.production.lot'].search([('id', 'in', lot_ids.ids),('product_id', '=', line.product_id.id)])
                        line_lotes += self.env['stock.production.lot'].search([('parent_lod_id', 'in', line_lotes.ids)])
                        quant_obj = self.env["stock.quant"] 
                        location_id = self.env["stock.location"].search([('usage', '=', 'internal')])
                        quants1 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', location_id.ids)])
                        scrap_loc_id = self.env["stock.location"].search([('scrap_location', '=', True)])
                        quants2 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', scrap_loc_id.ids)])
                        stock = sum([q.quantity for q in quants1])
                        scrap_qty = sum([q.quantity for q in quants2])
                        ventas_lines_lot_facturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lotes.ids),('invoice_status','=','invoiced')])
                        invoice_line_ids = []
                        for lin in ventas_lines_lot_facturadas:
                            invoice_line_ids.extend(lin.invoice_lines.ids)
                        invoice_line_ids = self.env['account.move.line'].search([('id', 'in', invoice_line_ids),('parent_state','!=', 'cancel')]) #,('parent_state','=', 'posted')
                        suma_cantidad_facturada = 0
                        suma_unidades_facturadas = 0
                        suma_unidades_por_facturadas = 0
                        ventas_lines_lot_porfacturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lotes.ids),('invoice_status','=','to invoice')])
                        for lin in ventas_lines_lot_porfacturadas:
                            suma_unidades_por_facturadas += lin.qty_delivered
                        for invoice_lin in invoice_line_ids:
                            if invoice_lin.parent_state == 'posted':
                                suma_cantidad_facturada += invoice_lin.credit
                                suma_unidades_facturadas += invoice_lin.quantity
                            else:
                                suma_unidades_por_facturadas += invoice_lin.quantity
                        if  suma_unidades_facturadas > 0:   
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': suma_unidades_facturadas,
                                'precio_prom': (suma_cantidad_facturada/suma_unidades_facturadas),
                                'total': suma_cantidad_facturada
                                }
                            tb_ventas.append(data_line)
                        if suma_unidades_por_facturadas > 0:
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': suma_unidades_por_facturadas,
                                'precio_prom': line.pending_invoice_price,
                                'total': (suma_unidades_por_facturadas*line.pending_invoice_price)
                                }
                            tb_porfacturar.append(data_line)
                        if stock > 0:
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': stock,
                                'precio_prom': line.current_stock_price,
                                'total': (stock*line.current_stock_price)
                                }
                            tb_stock.append(data_line)
                        if scrap_qty > 0:
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': scrap_qty,
                                }
                            tb_scrap.append(data_line)


                        #tabla de ventas final


                        display_name = line.product_id.display_name.replace(
                            ")", "").split("(")
                        variant = len(display_name) > 1 and display_name[1]
                        i += 1
                        sheet.write(i, 0, '', light_box)
                        sheet.write(i, 1, line.product_id.name, light_box)
                        sheet.write(i, 2, variant, light_box)
                        sheet.write(i, 3, line.box_rec, light_box)
                        sheet.write(i, 4, line.price_unit, light_box_currency)
                        sheet.write(i, 5, "=d{}*e{}".format(str(i+1), str(i+1)), light_box_currency)
                        sheet.write(i, 6, "", light_box_currency)
                        sheet.write(i, 7, "", light_box_currency)
                        sheet.write(i, 8, "", light_box_currency)
                        sheet.write(i, 9, "", light_box_currency)
                        sheet.write(i, 10, "=f{}*k{}".format(str(i+1), str(j)), light_box_currency)
                        sheet.write(i, 11, "=f{}-k{}".format(str(i+1), str(i+1)), light_box_currency)
                        final_i = i
                    for jj in range(9-(final_i - inicio_i)):
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
                        sheet.write(i, 11, '', light_box)
                        sumador = sumador +3
                    
                    #pintar tabla de ventas
                    tb_contador = 16
                    if len(tb_ventas) > 0:
                        sheet.write(tabla_ventas_inicial, tb_contador, 'Ventas', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+2, 'Precio', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+3, 'Total', report_format_gray)
                        contador = tabla_ventas_inicial + 1
                        for linea in tb_ventas:
                            sheet.write(contador, tb_contador, linea['product'], light_box)
                            sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
                            sheet.write(contador, tb_contador+2, linea['precio_prom'], light_box_currency)
                            sheet.write(contador, tb_contador+3, linea['total'], light_box_currency)
                            contador = contador + 1
                        tb_contador += 5

                    if len(tb_porfacturar) > 0:
                        sheet.write(tabla_ventas_inicial, tb_contador, 'Por Facturar', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+2, 'Precio', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+3, 'Total', report_format_gray)
                        contador = tabla_ventas_inicial + 1
                        for linea in tb_porfacturar:
                            sheet.write(contador, tb_contador, linea['product'], light_box)
                            sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
                            sheet.write(contador, tb_contador+2, linea['precio_prom'], light_box_currency)
                            sheet.write(contador, tb_contador+3, linea['total'], light_box_currency)
                            contador = contador + 1
                        tb_contador += 5

                    if len(tb_stock) > 0:
                        sheet.write(tabla_ventas_inicial, tb_contador, 'Stock', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+2, 'Precio', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+3, 'Total', report_format_gray)
                        contador = tabla_ventas_inicial + 1
                        for linea in tb_stock:
                            sheet.write(contador, tb_contador, linea['product'], light_box)
                            sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
                            sheet.write(contador, tb_contador+2, linea['precio_prom'], light_box_currency)
                            sheet.write(contador, tb_contador+3, linea['total'], light_box_currency)
                            contador = contador + 1
                        tb_contador += 5
                    
                    if len(tb_scrap) > 0:
                        sheet.write(tabla_ventas_inicial, tb_contador, 'Scrap', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
                        contador = tabla_ventas_inicial + 1
                        for linea in tb_scrap:
                            sheet.write(contador, tb_contador, linea['product'], light_box)
                            sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
                            contador = contador + 1
                        tb_contador += 5

                        #finaliza tabla de ventas
                    
                    sheet.write(i+1, 0, '', light_box)
                    sheet.write(i+1, 1, '', light_box)
                    sheet.write(i+1, 2, '', light_box)
                    sheet.write(i+1, 3, "", light_box)
                    sheet.write(i+1, 4, '', light_box)
                    sheet.write(i+1, 5, "=sum(f{}:f{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                    sheet.write(i+1, 3, "=sum(d{}:d{})".format(str(inicio_i+1), str(i+1)), light_box)
                    sheet.write(i+1, 6, settlement_id.freight_total, light_box_currency)
                    sheet.write(i+1, 7, settlement_id.aduana_total, light_box_currency)
                    sheet.write(i+1, 8, settlement_id.storage_total + settlement_id.maneuvers_total , light_box_currency)
                    sheet.write(i+1, 9, settlement_id.boxes , light_box_currency)
                    sheet.write(i+1, 10, "=sum(k{}:k{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                    sheet.write(i+1, 11, "=sum(l{}:l{})".format(str(inicio_i), str(i+1)), light_box_currency)
                    sheet.write(loc_total_gastos_row, 11, "=-(g{}+h{}+i{}+j{})".format(str(i+2), str(i+2),str(i+2),str(i+2)), light_box_currency)
                    sheet.write(liquidacion_ubicacion, 14, "=l{}".format(str(i+2)), travels_middle_right)
                    liquidaciones.append(liquidacion_ubicacion)
                    sheet.write(liquidacion_ubicacion+9, 14, "=(o{}+o{}+o{})-sum(o{}:o{})".format(str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion),str(liquidacion_ubicacion+1),str(liquidacion_ubicacion+9)), travels_middle_right)
                    sheet.write(liquidacion_ubicacion+11, 14, "=(o{}/(o{}+o{}+o{}))".format(str(liquidacion_ubicacion+10),str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion)), light_box_percentage)
                    i += 7

                    total_total += sale_update
                    total_porfacturar += exists_st.pending_invoice_value
                    total_stock += exists_st.stock_value
                    total_freight_in += freight_in_update
                    total_aduana_total += aduana_usa_update + aduana_mex_update
                    total_maneuvers_total += maneuvers_update
                    total_adjustment += adjustment_update
                    total_storage += storage_update
                    total_freight_out += freight_out_update
                    total_utility += settlement_id.utility
                    total_boxes += boxes_update

                    total_utility_percentage = float_round(settlement_id.utility_percentage, precision_digits=2)
                    utility_per_qty += 1
                    sumador = sumador + 15
                else:
                    po_product_ids = [line.product_id for line in po.order_line]
                    fecha = po.date_order
                    picking_ids = po.picking_ids.filtered(lambda picking: picking.state == 'done') # Se obtinenen pickings de la orden de compra
                    lot_ids = self.env["stock.production.lot"]
                    for sml in picking_ids.move_line_ids:
                        lot_ids += sml.lot_id
                    analytic_tag_ids = self.env['account.analytic.tag']
                    for lot in lot_ids:
                        tag = lot.analytic_tag_ids.filtered(lambda tag: len(tag.name)>5)
                        if not tag in analytic_tag_ids:
                            analytic_tag_ids += tag
                    move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
                    sales_lines = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.move_id.state == 'posted')
                    sales_ajust_lines = move_line_ids.filtered(lambda line: line.account_id.id in (1377, 1379) and line.move_id.state == 'posted')
                    freight_in = move_line_ids.filtered(lambda line: line.account_id.id == 1387 and line.move_id.state == 'posted')
                    freight_out = move_line_ids.filtered(lambda line: line.account_id.id == 1394 and line.move_id.state == 'posted')
                    maneuvers = move_line_ids.filtered(lambda line: line.account_id.id == 1390 and line.move_id.state == 'posted')
                    storage = move_line_ids.filtered(lambda line: line.account_id.id == 1395 and line.move_id.state == 'posted')
                    aduana_usa = move_line_ids.filtered(lambda line: line.account_id.id == 1393 and line.move_id.state == 'posted')
                    aduana_mex = move_line_ids.filtered(lambda line: line.account_id.id == 1392 and line.move_id.state == 'posted')#[]1392
                    adjustment = move_line_ids.filtered(lambda line: line.account_id.id == 1378 and line.move_id.state == 'posted')
                    boxes = move_line_ids.filtered(lambda line: line.account_id.id == 1509 and line.move_id.state == 'posted')
                    logistics = move_line_ids.filtered(lambda line: line.account_id.id == 1516 and line.move_id.state == 'posted')
                    sale_update = sum([sale.price_subtotal for sale in sales_lines])
                    sale_ajust_update = sum([sale.price_subtotal for sale in sales_ajust_lines])
                    sale_update = sale_update - sale_ajust_update
                    freight_in_update = sum([accline.price_subtotal for accline in freight_in])
                    freight_out_update = sum([accline.price_subtotal for accline in freight_out])
                    maneuvers_update = sum([accline.price_subtotal for accline in maneuvers])
                    storage_update = sum([accline.price_subtotal for accline in storage])
                    aduana_usa_update = sum([accline.price_subtotal for accline in aduana_usa])
                    aduana_mex_update = sum([accline.price_subtotal for accline in aduana_mex])
                    boxes_update = sum([accline.debit for accline in boxes])
                    logistics_update = sum([accline.debit for accline in logistics])
                    adjustment_update = sum([accline.price_subtotal for accline in adjustment])

                    exists_st.calcular_update()

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
                    #sheet.write(i+2, 6, '(-)Flete', light_header_top)
                    #sheet.write(i+2, 7, 'Aduana', light_header_top)
                    #sheet.write(i+2, 8, 'In&Out', light_header_top)
                    #sheet.write(i+2, 9, 'Boxes', light_header_top)
                    #sheet.write(i+2, 10, '(-)Comision', light_header_top)
                    sheet.write(i+2, 6, '', light_header_top)
                    
                    sheet.write(i+3, 0, 'Fecha', bold_header)
                    sheet.write(i+3, 1, 'Producto', light_header_bottom)
                    sheet.write(i+3, 2, 'Medida', light_header_bottom)
                    # sheet.write(7, 3, 'Emb.', light_header_bottom)
                    sheet.write(i+3, 3, 'Rec.', light_header_bottom)
                    sheet.write(i+3, 4, 'P.Unit.', light_header_bottom)
                    sheet.write(i+3, 5, 'Importe.', light_header_bottom)
                    #sheet.write(i+3, 6, '', light_header_bottom)
                    #sheet.write(i+3, 7, '', light_header_bottom)
                    #sheet.write(i+3, 8, '', light_header_bottom)
                    #sheet.write(i+3, 9, '', light_header_bottom)
                    #sheet.write(i+3, 10,"%d %%" % settlement_id.commission_percentage, light_header_bottom)
                    sheet.write(i+3, 6, 'Total', light_header_bottom)

                    sheet.write(i+5, 0, datestring, light_box)
                    
                    if len(procesar_object)> 1 or exists_st.actualizacion == True:
                        sheet.write(i, 8, 'Viaje', travels)
                        sheet.write(i + 1, 8, 'VENTAS', travels_title_top_left)
                        sheet.write(i + 2, 8, 'POR FACTURAR', travels_middle_left)
                        sheet.write(i + 3, 8, 'STOCK', travels_middle_left)
                        sheet.write(i + 4, 8, 'LIQUIDACIONES', travels_middle_left)
                        sheet.write(i + 5, 8, 'Freight In', travels_middle_left)
                        sheet.write(i + 6, 8, 'Aduana', travels_middle_left)
                        sheet.write(i + 7, 8, 'MANIOBRAS', travels_middle_left_red)
                        sheet.write(i + 8, 8, 'AJUSTE', travels_middle_left_red)
                        sheet.write(i + 9, 8, 'STORAGE', travels_middle_left_red)
                        sheet.write(i + 10, 8, 'FREIGHT OUT', travels_middle_left_red)
                        sheet.write(i + 11, 8, 'CAJAS', travels_middle_left_red)
                        sheet.write(i + 12, 8, 'LOGISTICS', travels_middle_left_red)
                        sheet.write(i + 13, 8, 'UTILIDAD', travels_middle_left)
                        sheet.write(i, 9, po.name, name)
                        sheet.write(i + 1, 9, sale_update, travels_title_top_right)
                        sheet.write(i + 2, 9, exists_st.pending_invoice_value, travels_middle_right)
                        sheet.write(i + 3, 9, exists_st.stock_value, travels_middle_right)
                        sheet.write(i + 5, 9, freight_in_update, travels_middle_right)
                        sheet.write(i + 6, 9, aduana_usa_update+aduana_mex_update, travels_middle_right)
                        sheet.write(i + 7, 9, maneuvers_update, travels_middle_right_red)
                        sheet.write(i + 8, 9, adjustment_update, travels_middle_right_red)
                        sheet.write(i + 9, 9, storage_update, travels_middle_right_red)
                        sheet.write(i + 10, 9, freight_out_update, travels_middle_right_red)
                        sheet.write(i + 11, 9, boxes_update, travels_middle_right_red)
                        sheet.write(i + 12, 9, logistics_update, travels_middle_right_red)
                        sheet.write(i + 13, 9, settlement_id.utility, travels_middle_right)
                        sheet.write(i + 15, 9, str(float_round(settlement_id.utility_percentage, precision_digits=2)) + "%", travels_bottom_right)
                        #sheet.write(i + 2, 13, '', travels_middle_left)
                        #sheet.write(i + 3, 13, '', travels_middle_left)
                        #sheet.write(i + 11, 13, '', travels_middle_left)
                        #sheet.write(i + 12, 8, '', travels_middle_left)
                        sheet.write(i + 14, 8, '', travels_middle_left)
                        #sheet.write(i + 2, 14, '', travels_middle_right)
                        #sheet.write(i + 3, 14, '', travels_middle_right)
                        sheet.write(i + 4, 9, settlement_id.settlement, travels_middle_right)
                        #sheet.write(i + 11, 14, '', travels_middle_right)
                        #sheet.write(i + 12, 9, '', travels_middle_right)
                        sheet.write(i + 14, 9, '', travels_middle_right)
                        sheet.write(i + 15, 8, '', travels_bottom_left)
                    
                    exists_st.actualizacion = True
                    liquidacion_ubicacion = i + 4
                    tabla_ventas_inicial =  i + 5
                    i += 5
                    j = i - 1
                    inicio_i = i
                    final_i = i
                    #activar variables para cuadro vde ventas
                    tb_ventas = []
                    tb_porfacturar = []
                    tb_stock = []
                    tb_scrap = []

                    #sheet.write(i - 1, 11, (-settlement_id.freight_total-settlement_id.aduana_total-settlement_id.storage_total-settlement_id.maneuvers_total-settlement_id.boxes), light_box_currency)
                    for line in settlement_id.settlements_line_ids:

                        #tabla de ventas inicio
                        line_lotes =  self.env['stock.production.lot'].search([('id', 'in', lot_ids.ids),('product_id', '=', line.product_id.id)])
                        line_lotes += self.env['stock.production.lot'].search([('parent_lod_id', 'in', line_lotes.ids)])
                        quant_obj = self.env["stock.quant"] 
                        location_id = self.env["stock.location"].search([('usage', '=', 'internal')])
                        quants1 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', location_id.ids)])
                        scrap_loc_id = self.env["stock.location"].search([('scrap_location', '=', True)])
                        quants2 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', scrap_loc_id.ids)])
                        stock = sum([q.quantity for q in quants1])
                        scrap_qty = sum([q.quantity for q in quants2])
                        ventas_lines_lot_facturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lotes.ids),('invoice_status','=','invoiced')])
                        invoice_line_ids = []
                        for lin in ventas_lines_lot_facturadas:
                            invoice_line_ids.extend(lin.invoice_lines.ids)
                        invoice_line_ids = self.env['account.move.line'].search([('id', 'in', invoice_line_ids),('parent_state','!=', 'cancel')]) #,('parent_state','=', 'posted')
                        suma_cantidad_facturada = 0
                        suma_unidades_facturadas = 0
                        suma_unidades_por_facturadas = 0
                        ventas_lines_lot_porfacturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lotes.ids),('invoice_status','=','to invoice')])
                        for lin in ventas_lines_lot_porfacturadas:
                            suma_unidades_por_facturadas += lin.qty_delivered
                        for invoice_lin in invoice_line_ids:
                            if invoice_lin.parent_state == 'posted':
                                suma_cantidad_facturada += invoice_lin.credit
                                suma_unidades_facturadas += invoice_lin.quantity
                            else:
                                suma_unidades_por_facturadas += invoice_lin.quantity
                        if  suma_unidades_facturadas > 0:   
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': suma_unidades_facturadas,
                                'precio_prom': (suma_cantidad_facturada/suma_unidades_facturadas),
                                'total': suma_cantidad_facturada
                                }
                            tb_ventas.append(data_line)
                        if suma_unidades_por_facturadas > 0:
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': suma_unidades_por_facturadas,
                                'precio_prom': line.pending_invoice_price,
                                'total': (suma_unidades_por_facturadas*line.pending_invoice_price)
                                }
                            tb_porfacturar.append(data_line)
                        if stock > 0:
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': stock,
                                'precio_prom': line.current_stock_price,
                                'total': (stock*line.current_stock_price)
                                }
                            tb_stock.append(data_line)
                        if scrap_qty > 0:
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': scrap_qty,
                                }
                            tb_scrap.append(data_line)


                        #tabla de ventas final    


                        display_name = line.product_id.display_name.replace(
                            ")", "").split("(")
                        variant = len(display_name) > 1 and display_name[1]
                        i += 1
                        sheet.write(i, 0, '', light_box)
                        sheet.write(i, 1, line.product_id.name, light_box)
                        sheet.write(i, 2, variant, light_box)
                        sheet.write(i, 3, line.box_rec, light_box)
                        sheet.write(i, 4, line.price_unit, light_box_currency) #buscar precio original
                        sheet.write(i, 5, "=d{}*e{}".format(str(i+1), str(i+1)), light_box_currency)
                        #sheet.write(i, 6, "", light_box_currency)
                        #sheet.write(i, 7, "", light_box_currency)
                        #sheet.write(i, 8, "", light_box_currency)
                        #sheet.write(i, 9, "", light_box_currency)
                        #sheet.write(i, 10, "=f{}*k{}".format(str(i+1), str(j)), light_box_currency)
                        sheet.write(i, 6, "=f{}".format(str(i+1)), light_box_currency)
                        final_i = i
                    for jj in range(9-(final_i - inicio_i)):
                        i += 1
                        sheet.write(i, 0, '', light_box)
                        sheet.write(i, 1, '', light_box)
                        sheet.write(i, 2, '', light_box)
                        sheet.write(i, 3, '', light_box)
                        sheet.write(i, 4, '', light_box)
                        sheet.write(i, 5, '', light_box)
                        sheet.write(i, 6, '', light_box)
                        #sheet.write(i, 7, '', light_box)
                        #sheet.write(i, 8, '', light_box)
                        #sheet.write(i, 9, '', light_box)
                        #sheet.write(i, 10, '', light_box)
                        #sheet.write(i, 11, '', light_box)
                        sumador = sumador +3

                    
                    #pintar tabla de ventas
                    tb_contador = 11
                    if len(tb_ventas) > 0:
                        sheet.write(tabla_ventas_inicial, tb_contador, 'Ventas', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+2, 'Precio', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+3, 'Total', report_format_gray)
                        contador = tabla_ventas_inicial + 1
                        for linea in tb_ventas:
                            sheet.write(contador, tb_contador, linea['product'], light_box)
                            sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
                            sheet.write(contador, tb_contador+2, linea['precio_prom'], light_box_currency)
                            sheet.write(contador, tb_contador+3, linea['total'], light_box_currency)
                            contador = contador + 1
                        tb_contador += 5

                    if len(tb_porfacturar) > 0:
                        sheet.write(tabla_ventas_inicial, tb_contador, 'Por Facturar', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+2, 'Precio', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+3, 'Total', report_format_gray)
                        contador = tabla_ventas_inicial + 1
                        for linea in tb_porfacturar:
                            sheet.write(contador, tb_contador, linea['product'], light_box)
                            sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
                            sheet.write(contador, tb_contador+2, linea['precio_prom'], light_box_currency)
                            sheet.write(contador, tb_contador+3, linea['total'], light_box_currency)
                            contador = contador + 1
                        tb_contador += 5

                    if len(tb_stock) > 0:
                        sheet.write(tabla_ventas_inicial, tb_contador, 'Stock', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+2, 'Precio', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+3, 'Total', report_format_gray)
                        contador = tabla_ventas_inicial + 1
                        for linea in tb_stock:
                            sheet.write(contador, tb_contador, linea['product'], light_box)
                            sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
                            sheet.write(contador, tb_contador+2, linea['precio_prom'], light_box_currency)
                            sheet.write(contador, tb_contador+3, linea['total'], light_box_currency)
                            contador = contador + 1
                        tb_contador += 5
                    
                    if len(tb_scrap) > 0:
                        sheet.write(tabla_ventas_inicial, tb_contador, 'Scrap', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
                        contador = tabla_ventas_inicial + 1
                        for linea in tb_scrap:
                            sheet.write(contador, tb_contador, linea['product'], light_box)
                            sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
                            contador = contador + 1
                        tb_contador += 5

                    #finaliza tabla de ventas
                    
                    
                    sheet.write(i+1, 0, '', light_box)
                    sheet.write(i+1, 1, '', light_box)
                    sheet.write(i+1, 2, '', light_box)
                    sheet.write(i+1, 4, "", light_box)
                    sheet.write(i+1, 3, "=sum(d{}:d{})".format(str(inicio_i+1), str(i+1)), light_box)
                    sheet.write(i+1, 5, "=sum(f{}:f{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                    #sheet.write(i+1, 6, settlement_id.freight_total, light_box_currency)
                    #sheet.write(i+1, 7, settlement_id.aduana_total, light_box_currency)
                    #sheet.write(i+1, 8, settlement_id.storage_total + settlement_id.maneuvers_total , light_box_currency)
                    #sheet.write(i+1, 9, settlement_id.boxes , light_box_currency)
                    #sheet.write(i+1, 10, "=sum(k{}:k{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                    sheet.write(i+1, 6, "=sum(g{}:g{})".format(str(inicio_i), str(i+1)), light_box_currency)
                    sheet.write(liquidacion_ubicacion, 9, "=g{}".format(str(i+2)), travels_middle_right)
                    liquidaciones.append(liquidacion_ubicacion)
                    sheet.write(liquidacion_ubicacion+9, 9, "=(j{}+j{}+j{})-sum(j{}:j{})".format(str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion),str(liquidacion_ubicacion+1),str(liquidacion_ubicacion+9)), travels_middle_right)
                    sheet.write(liquidacion_ubicacion+11, 9, "=(j{}/(j{}+j{}+j{}))".format(str(liquidacion_ubicacion+10),str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion)), light_box_percentage)
                    i += 7

                    total_total += sale_update
                    total_porfacturar += exists_st.pending_invoice_value
                    total_stock += exists_st.stock_value
                    total_freight_in += freight_in_update
                    total_aduana_total += aduana_usa_update + aduana_mex_update
                    total_maneuvers_total += maneuvers_update
                    total_adjustment += adjustment_update
                    total_storage += storage_update
                    total_freight_out += freight_out_update
                    total_utility += settlement_id.utility
                    total_boxes += boxes_update

                    total_utility_percentage = float_round(settlement_id.utility_percentage, precision_digits=2)
                    utility_per_qty += 1
                    sumador = sumador + 15

                #aqui va a terminar el if de tipo de liquidacion
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
                sheet.write(i+1, 9, '', light_header_bottom)
                sheet.write(i+2, 0, 'Sin liquidación', report_format)
                i += 3
                
        formula_liquidacion = "=("
        for liq in liquidaciones:
            formula_liquidacion += "+o{}".format(str(liq+1))
        formula_liquidacion += ")"
        i += 1
        if len(procesar_object)>1:
            sheet.write(i, 13, 'TOTALES', travels)
            sheet.write(i + 1, 13, 'VENTAS', travels_title_top_left)
            sheet.write(i + 2, 13, 'POR FACTURAR', travels_middle_left)
            sheet.write(i + 3, 13, 'STOCK', travels_middle_left)
            sheet.write(i + 4, 13, 'LIQUIDACIONES', travels_middle_left)
            sheet.write(i + 5, 13, 'Freight In', travels_middle_left)
            sheet.write(i + 6, 13, 'Aduana', travels_middle_left)
            sheet.write(i + 7, 13, 'MANIOBRAS', travels_middle_left_red)
            sheet.write(i + 8, 13, 'AJUSTE', travels_middle_left_red)
            sheet.write(i + 9, 13, 'STORAGE', travels_middle_left_red)
            sheet.write(i + 10, 13, 'FREIGHT OUT', travels_middle_left_red)
            sheet.write(i + 13, 13, 'UTILIDAD', travels_middle_left)
            sheet.write(i + 11, 13, 'CAJAS', travels_middle_left)
            sheet.write(i + 12, 13, 'LOGISTICS', travels_middle_left)
            sheet.write(i + 1, 14, total_total, travels_title_top_right)
            sheet.write(i + 2, 14, total_porfacturar , travels_middle_right)
            sheet.write(i + 3, 14, total_stock, travels_middle_right)
            sheet.write(i + 4, 14, formula_liquidacion, travels_middle_right)
            sheet.write(i + 5, 14, total_freight_in, travels_middle_right)
            sheet.write(i + 6, 14, total_aduana_total, travels_middle_right)
            sheet.write(i + 7, 14, total_maneuvers_total, travels_middle_right_red)
            sheet.write(i + 8, 14, total_adjustment, travels_middle_right_red)
            sheet.write(i + 9, 14, total_storage, travels_middle_right_red)
            sheet.write(i + 10, 14, total_freight_out , travels_middle_right_red)
            sheet.write(i + 11, 14, total_boxes, travels_middle_right_red)
            sheet.write(i + 13, 14, "=(o{}+o{}+o{})-sum(o{}:o{})".format(str(i+2),str(i+3),str(i+4),str(i+5),str(i+13)), travels_middle_right)
            sheet.write(i + 15, 14, "=(o{}/(o{}+o{}+o{}))".format(str(i+14),str(i+2),str(i+3),str(i+4)), light_box_percentage)

            #sheet.write(i + 2, 13, '', travels_middle_left)
            #sheet.write(i + 3, 13, '', travels_middle_left)
            #sheet.write(i + 11, 1, '', travels_middle_left)
            sheet.write(i + 12, 13, '', travels_middle_left)
            sheet.write(i + 14, 13, '', travels_middle_left)
            #sheet.write(i + 2, 14, '', travels_middle_right)
            #sheet.write(i + 3, 14, '', travels_middle_right)
            #sheet.write(i + 4, 14, '', travels_middle_right)
            #sheet.write(i + 11, 2, '', travels_middle_right)
            #sheet.write(i + 12, 14, '', travels_middle_right)
            #sheet.write(i + 14, 14, '', travels_middle_right)
            #sheet.write(i + 15, 14, '', travels_bottom_left)


class XlsxUtilityReport_firma(models.AbstractModel):    
    _name = 'report.liquidaciones.xlsx_utility_report_firma'
    _inherit = 'report.odoo_report_xlsx.abstract'

    def _get_objs_for_report(self, docids, data):
        if docids:
            ids = docids
        elif data and 'context' in data:
            ids = data["context"].get('active_ids', [])
        else:
            ids = self.env.context.get('active_ids', [])
        if docids:
            return self.env['purchase.order'].browse(ids)
        else:
            return self.env['sale.settlements'].browse(ids)

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
        sumador = i
        inicio_i = 0
        total_total = 0
        total_freight_in = 0
        total_aduana_total = 0
        total_maneuvers_total = 0
        total_adjustment = 0
        total_storage = 0
        total_freight_out = 0
        total_boxes = 0
        total_utility = 0
        total_utility_percentage = 0
        total_porfacturar = 0
        total_stock = 0
        utility_per_qty = 0
        liquidaciones = []

        if type(objects) == type(self.env['sale.settlements']):
            procesar_object = objects[0].order_id
        elif type(objects) == type(self.env['purchase.order']):
            procesar_object = objects

        for po in procesar_object:
            exists_st = self.env['sale.settlements'].search([('order_id', '=', po.id)], limit=1)
            if exists_st:
                if exists_st.price_type == 'open':
                    #codigo para determinar datos actualizables
                    po_product_ids = [line.product_id for line in po.order_line]
                    fecha = po.date_order
                    picking_ids = po.picking_ids.filtered(lambda picking: picking.state == 'done') # Se obtinenen pickings de la orden de compra
                    lot_ids = self.env["stock.production.lot"]
                    for sml in picking_ids.move_line_ids:
                        lot_ids += sml.lot_id
                    analytic_tag_ids = self.env['account.analytic.tag']
                    for lot in lot_ids:
                        tag = lot.analytic_tag_ids.filtered(lambda tag: len(tag.name)>5)
                        if not tag in analytic_tag_ids:
                            analytic_tag_ids += tag
                    move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
                    sales_lines = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.move_id.state == 'posted')
                    sales_ajust_lines = move_line_ids.filtered(lambda line: line.account_id.id in (1377, 1379) and line.move_id.state == 'posted')
                    freight_in = move_line_ids.filtered(lambda line: line.account_id.id == 1387 and line.move_id.state == 'posted')
                    freight_out = move_line_ids.filtered(lambda line: line.account_id.id == 1394 and line.move_id.state == 'posted')
                    maneuvers = move_line_ids.filtered(lambda line: line.account_id.id == 1390 and line.move_id.state == 'posted')
                    storage = move_line_ids.filtered(lambda line: line.account_id.id == 1395 and line.move_id.state == 'posted')
                    aduana_usa = move_line_ids.filtered(lambda line: line.account_id.id == 1393 and line.move_id.state == 'posted')
                    aduana_mex = move_line_ids.filtered(lambda line: line.account_id.id == 1392 and line.move_id.state == 'posted')#[]1392
                    adjustment = move_line_ids.filtered(lambda line: line.account_id.id == 1378 and line.move_id.state == 'posted')
                    boxes = move_line_ids.filtered(lambda line: line.account_id.id == 1509 and line.move_id.state == 'posted')
                    sale_update = sum([sale.price_subtotal for sale in sales_lines])
                    sale_ajust_update = sum([sale.price_subtotal for sale in sales_ajust_lines])
                    sale_update = sale_update - sale_ajust_update
                    freight_in_update = sum([accline.price_subtotal for accline in freight_in])
                    freight_out_update = sum([accline.price_subtotal for accline in freight_out])
                    maneuvers_update = sum([accline.price_subtotal for accline in maneuvers])
                    storage_update = sum([accline.price_subtotal for accline in storage])
                    aduana_usa_update = sum([accline.price_subtotal for accline in aduana_usa])
                    aduana_mex_update = sum([accline.price_subtotal for accline in aduana_mex])
                    boxes_update = sum([accline.debit for accline in boxes])
                    adjustment_update = sum([accline.price_subtotal for accline in adjustment])

                    exists_st.calcular_update()

                    #termina datos actualizables

                    #aqui poner el if para open close
                    settlement_id = exists_st
                    lang = self.env.user.lang
                    lang_id = self.env['res.lang'].search([('code', '=', lang)])
                    datestring = fields.Date.from_string(str(po.date_order)).strftime(lang_id.date_format)

                    crear_tabla_ziquierda(sheet, i, settlement_id)
                    #inicia tabla liquidacion izquiersa
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
                    sheet.write(i+2, 9, 'Boxes', light_header_top)
                    sheet.write(i+2, 10, '(-)Comision', light_header_top)
                    sheet.write(i+2, 11, '', light_header_top)
                    
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
                    sheet.write(i+3, 9, '', light_header_bottom)
                    sheet.write(
                        i+3, 10,
                        "%d %%" % settlement_id.commission_percentage,
                        light_header_bottom)
                    sheet.write(i+3, 11, 'Total', light_header_bottom)

                    sheet.write(i+5, 0, datestring, light_box)
                    
                    exists_st.actualizacion = True
                    tabla_ventas_inicial =  i + 5
                    liquidacion_ubicacion = i + 4
                    i += 5
                    j = i - 1
                    inicio_i = i
                    final_i = i
                    sheet.write(i - 1, 11, (-settlement_id.freight_total-settlement_id.aduana_total-settlement_id.storage_total-settlement_id.maneuvers_total-settlement_id.boxes), light_box_currency)
                    #activar variables para cuadro vde ventas
                    tb_ventas = []
                    tb_porfacturar = []
                    tb_stock = []
                    tb_scrap = []

                    for line in settlement_id.settlements_line_ids:
                        #tabla de ventas inicio
                        line_lotes =  self.env['stock.production.lot'].search([('id', 'in', lot_ids.ids),('product_id', '=', line.product_id.id)])
                        line_lotes += self.env['stock.production.lot'].search([('parent_lod_id', 'in', line_lotes.ids)])
                        quant_obj = self.env["stock.quant"] 
                        location_id = self.env["stock.location"].search([('usage', '=', 'internal')])
                        quants1 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', location_id.ids)])
                        scrap_loc_id = self.env["stock.location"].search([('scrap_location', '=', True)])
                        quants2 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', scrap_loc_id.ids)])
                        stock = sum([q.quantity for q in quants1])
                        scrap_qty = sum([q.quantity for q in quants2])
                        ventas_lines_lot_facturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lotes.ids),('invoice_status','=','invoiced')])
                        invoice_line_ids = []
                        for lin in ventas_lines_lot_facturadas:
                            invoice_line_ids.extend(lin.invoice_lines.ids)
                        invoice_line_ids = self.env['account.move.line'].search([('id', 'in', invoice_line_ids),('parent_state','!=', 'cancel')]) #,('parent_state','=', 'posted')
                        suma_cantidad_facturada = 0
                        suma_unidades_facturadas = 0
                        suma_unidades_por_facturadas = 0
                        ventas_lines_lot_porfacturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lotes.ids),('invoice_status','=','to invoice')])
                        for lin in ventas_lines_lot_porfacturadas:
                            suma_unidades_por_facturadas += lin.qty_delivered
                        for invoice_lin in invoice_line_ids:
                            if invoice_lin.parent_state == 'posted':
                                suma_cantidad_facturada += invoice_lin.credit
                                suma_unidades_facturadas += invoice_lin.quantity
                            else:
                                suma_unidades_por_facturadas += invoice_lin.quantity
                        if  suma_unidades_facturadas > 0:   
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': suma_unidades_facturadas,
                                'precio_prom': (suma_cantidad_facturada/suma_unidades_facturadas),
                                'total': suma_cantidad_facturada
                                }
                            tb_ventas.append(data_line)
                        if suma_unidades_por_facturadas > 0:
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': suma_unidades_por_facturadas,
                                'precio_prom': line.pending_invoice_price,
                                'total': (suma_unidades_por_facturadas*line.pending_invoice_price)
                                }
                            tb_porfacturar.append(data_line)
                        if stock > 0:
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': stock,
                                'precio_prom': line.current_stock_price,
                                'total': (stock*line.current_stock_price)
                                }
                            tb_stock.append(data_line)
                        if scrap_qty > 0:
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': scrap_qty,
                                }
                            tb_scrap.append(data_line)


                        #tabla de ventas final


                        display_name = line.product_id.display_name.replace(
                            ")", "").split("(")
                        variant = len(display_name) > 1 and display_name[1]
                        i += 1
                        sheet.write(i, 0, '', light_box)
                        sheet.write(i, 1, line.product_id.name, light_box)
                        sheet.write(i, 2, variant, light_box)
                        sheet.write(i, 3, line.box_rec, light_box)
                        sheet.write(i, 4, line.price_unit, light_box_currency)
                        sheet.write(i, 5, "=d{}*e{}".format(str(i+1), str(i+1)), light_box_currency)
                        sheet.write(i, 6, "", light_box_currency)
                        sheet.write(i, 7, "", light_box_currency)
                        sheet.write(i, 8, "", light_box_currency)
                        sheet.write(i, 9, "", light_box_currency)
                        sheet.write(i, 10, "=f{}*k{}".format(str(i+1), str(j)), light_box_currency)
                        sheet.write(i, 11, "=f{}-k{}".format(str(i+1), str(i+1)), light_box_currency)
                        final_i = i
                    for jj in range(9-(final_i - inicio_i)):
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
                        sheet.write(i, 11, '', light_box)
                        sumador = sumador +3
                    
                    
                    
                    sheet.write(i+1, 0, '', light_box)
                    sheet.write(i+1, 1, '', light_box)
                    sheet.write(i+1, 2, '', light_box)
                    sheet.write(i+1, 3, "", light_box)
                    sheet.write(i+1, 4, '', light_box)
                    sheet.write(i+1, 5, "=sum(f{}:f{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                    sheet.write(i+1, 6, settlement_id.freight_total, light_box_currency)
                    sheet.write(i+1, 7, settlement_id.aduana_total, light_box_currency)
                    sheet.write(i+1, 8, settlement_id.storage_total + settlement_id.maneuvers_total , light_box_currency)
                    sheet.write(i+1, 9, settlement_id.boxes , light_box_currency)
                    sheet.write(i+1, 10, "=sum(k{}:k{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                    sheet.write(i+1, 11, "=sum(l{}:l{})".format(str(inicio_i), str(i+1)), light_box_currency)
                    sheet.write(liquidacion_ubicacion, 14, "=l{}".format(str(i+2)), travels_middle_right)
                    liquidaciones.append(liquidacion_ubicacion)
                    sheet.write(liquidacion_ubicacion+9, 14, "=(o{}+o{}+o{})-sum(o{}:o{})".format(str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion),str(liquidacion_ubicacion+1),str(liquidacion_ubicacion+9)), travels_middle_right)
                    sheet.write(liquidacion_ubicacion+11, 14, "=(o{}/(o{}+o{}+o{}))".format(str(liquidacion_ubicacion+10),str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion)), travels_middle_right)
                    i += 7

                    total_total += sale_update
                    total_porfacturar += exists_st.pending_invoice_value
                    total_stock += exists_st.stock_value
                    total_freight_in += freight_in_update
                    total_aduana_total += aduana_usa_update + aduana_mex_update
                    total_maneuvers_total += maneuvers_update
                    total_adjustment += adjustment_update
                    total_storage += storage_update
                    total_freight_out += freight_out_update
                    total_utility += settlement_id.utility
                    total_boxes += boxes_update

                    total_utility_percentage = float_round(settlement_id.utility_percentage, precision_digits=2)
                    utility_per_qty += 1
                    sumador = sumador + 15
                else:
                    po_product_ids = [line.product_id for line in po.order_line]
                    fecha = po.date_order
                    picking_ids = po.picking_ids.filtered(lambda picking: picking.state == 'done') # Se obtinenen pickings de la orden de compra
                    lot_ids = self.env["stock.production.lot"]
                    for sml in picking_ids.move_line_ids:
                        lot_ids += sml.lot_id
                    analytic_tag_ids = self.env['account.analytic.tag']
                    for lot in lot_ids:
                        tag = lot.analytic_tag_ids.filtered(lambda tag: len(tag.name)>5)
                        if not tag in analytic_tag_ids:
                            analytic_tag_ids += tag
                    move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
                    sales_lines = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.move_id.state == 'posted')
                    sales_ajust_lines = move_line_ids.filtered(lambda line: line.account_id.id in (1377, 1379) and line.move_id.state == 'posted')
                    freight_in = move_line_ids.filtered(lambda line: line.account_id.id == 1387 and line.move_id.state == 'posted')
                    freight_out = move_line_ids.filtered(lambda line: line.account_id.id == 1394 and line.move_id.state == 'posted')
                    maneuvers = move_line_ids.filtered(lambda line: line.account_id.id == 1390 and line.move_id.state == 'posted')
                    storage = move_line_ids.filtered(lambda line: line.account_id.id == 1395 and line.move_id.state == 'posted')
                    aduana_usa = move_line_ids.filtered(lambda line: line.account_id.id == 1393 and line.move_id.state == 'posted')
                    aduana_mex = move_line_ids.filtered(lambda line: line.account_id.id == 1392 and line.move_id.state == 'posted')#[]1392
                    adjustment = move_line_ids.filtered(lambda line: line.account_id.id == 1378 and line.move_id.state == 'posted')
                    boxes = move_line_ids.filtered(lambda line: line.account_id.id == 1509 and line.move_id.state == 'posted')
                    sale_update = sum([sale.price_subtotal for sale in sales_lines])
                    sale_ajust_update = sum([sale.price_subtotal for sale in sales_ajust_lines])
                    sale_update = sale_update - sale_ajust_update
                    freight_in_update = sum([accline.price_subtotal for accline in freight_in])
                    freight_out_update = sum([accline.price_subtotal for accline in freight_out])
                    maneuvers_update = sum([accline.price_subtotal for accline in maneuvers])
                    storage_update = sum([accline.price_subtotal for accline in storage])
                    aduana_usa_update = sum([accline.price_subtotal for accline in aduana_usa])
                    aduana_mex_update = sum([accline.price_subtotal for accline in aduana_mex])
                    boxes_update = sum([accline.debit for accline in boxes])
                    adjustment_update = sum([accline.price_subtotal for accline in adjustment])

                    exists_st.calcular_update()

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
                    #sheet.write(i+2, 6, '(-)Flete', light_header_top)
                    #sheet.write(i+2, 7, 'Aduana', light_header_top)
                    #sheet.write(i+2, 8, 'In&Out', light_header_top)
                    #sheet.write(i+2, 9, 'Boxes', light_header_top)
                    #sheet.write(i+2, 10, '(-)Comision', light_header_top)
                    sheet.write(i+2, 6, '', light_header_top)
                    
                    sheet.write(i+3, 0, 'Fecha', bold_header)
                    sheet.write(i+3, 1, 'Producto', light_header_bottom)
                    sheet.write(i+3, 2, 'Medida', light_header_bottom)
                    # sheet.write(7, 3, 'Emb.', light_header_bottom)
                    sheet.write(i+3, 3, 'Rec.', light_header_bottom)
                    sheet.write(i+3, 4, 'P.Unit.', light_header_bottom)
                    sheet.write(i+3, 5, 'Importe.', light_header_bottom)
                    #sheet.write(i+3, 6, '', light_header_bottom)
                    #sheet.write(i+3, 7, '', light_header_bottom)
                    #sheet.write(i+3, 8, '', light_header_bottom)
                    #sheet.write(i+3, 9, '', light_header_bottom)
                    #sheet.write(i+3, 10,"%d %%" % settlement_id.commission_percentage, light_header_bottom)
                    sheet.write(i+3, 6, 'Total', light_header_bottom)

                    sheet.write(i+5, 0, datestring, light_box)
                    
                    if len(procesar_object)> 1 or exists_st.actualizacion == True:
                        sheet.write(i, 8, 'Viaje', travels)
                        sheet.write(i + 1, 8, 'VENTAS', travels_title_top_left)
                        sheet.write(i + 2, 8, 'POR FACTURAR', travels_title_top_left)
                        sheet.write(i + 3, 8, 'STOCK', travels_title_top_left)
                        sheet.write(i + 4, 8, 'LIQUIDACIONES', travels_middle_left)
                        sheet.write(i + 5, 8, 'Freight In', travels_middle_left)
                        sheet.write(i + 6, 8, 'Aduana', travels_middle_left)
                        sheet.write(i + 7, 8, 'MANIOBRAS', travels_middle_left_red)
                        sheet.write(i + 8, 8, 'AJUSTE', travels_middle_left_red)
                        sheet.write(i + 9, 8, 'STORAGE', travels_middle_left_red)
                        sheet.write(i + 10, 8, 'FREIGHT OUT', travels_middle_left_red)
                        sheet.write(i + 11, 8, 'CAJAS', travels_middle_left_red)
                        sheet.write(i + 13, 8, 'UTILIDAD', travels_middle_left)
                        sheet.write(i, 9, po.name, name)
                        sheet.write(i + 1, 9, sale_update, travels_title_top_right)
                        sheet.write(i + 2, 9, exists_st.pending_invoice_value, travels_middle_right)
                        sheet.write(i + 3, 9, exists_st.stock_value, travels_middle_right)
                        sheet.write(i + 5, 9, freight_in_update, travels_middle_right)
                        sheet.write(i + 6, 9, aduana_usa_update+aduana_mex_update, travels_middle_right)
                        sheet.write(i + 7, 9, maneuvers_update, travels_middle_right_red)
                        sheet.write(i + 8, 9, adjustment_update, travels_middle_right_red)
                        sheet.write(i + 9, 9, storage_update, travels_middle_right_red)
                        sheet.write(i + 10, 9, freight_out_update, travels_middle_right_red)
                        sheet.write(i + 11, 9, boxes_update, travels_middle_right_red)
                        sheet.write(i + 13, 9, settlement_id.utility, travels_middle_right)
                        sheet.write(i + 15, 9, str(float_round(settlement_id.utility_percentage, precision_digits=2)) + "%", travels_bottom_right)
                        #sheet.write(i + 2, 13, '', travels_middle_left)
                        #sheet.write(i + 3, 13, '', travels_middle_left)
                        #sheet.write(i + 11, 13, '', travels_middle_left)
                        sheet.write(i + 12, 8, '', travels_middle_left)
                        sheet.write(i + 14, 8, '', travels_middle_left)
                        #sheet.write(i + 2, 14, '', travels_middle_right)
                        #sheet.write(i + 3, 14, '', travels_middle_right)
                        sheet.write(i + 4, 9, settlement_id.settlement, travels_middle_right)
                        #sheet.write(i + 11, 14, '', travels_middle_right)
                        sheet.write(i + 12, 9, '', travels_middle_right)
                        sheet.write(i + 14, 9, '', travels_middle_right)
                        sheet.write(i + 15, 8, '', travels_bottom_left)
                    
                    exists_st.actualizacion = True
                    liquidacion_ubicacion = i + 4
                    tabla_ventas_inicial =  i + 5
                    i += 5
                    j = i - 1
                    inicio_i = i
                    final_i = i
                    #activar variables para cuadro vde ventas
                    tb_ventas = []
                    tb_porfacturar = []
                    tb_stock = []
                    tb_scrap = []

                    #sheet.write(i - 1, 11, (-settlement_id.freight_total-settlement_id.aduana_total-settlement_id.storage_total-settlement_id.maneuvers_total-settlement_id.boxes), light_box_currency)
                    for line in settlement_id.settlements_line_ids:

                        #tabla de ventas inicio
                        line_lotes =  self.env['stock.production.lot'].search([('id', 'in', lot_ids.ids),('product_id', '=', line.product_id.id)])
                        line_lotes += self.env['stock.production.lot'].search([('parent_lod_id', 'in', line_lotes.ids)])
                        quant_obj = self.env["stock.quant"] 
                        location_id = self.env["stock.location"].search([('usage', '=', 'internal')])
                        quants1 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', location_id.ids)])
                        scrap_loc_id = self.env["stock.location"].search([('scrap_location', '=', True)])
                        quants2 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', scrap_loc_id.ids)])
                        stock = sum([q.quantity for q in quants1])
                        scrap_qty = sum([q.quantity for q in quants2])
                        ventas_lines_lot_facturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lotes.ids),('invoice_status','=','invoiced')])
                        invoice_line_ids = []
                        for lin in ventas_lines_lot_facturadas:
                            invoice_line_ids.extend(lin.invoice_lines.ids)
                        invoice_line_ids = self.env['account.move.line'].search([('id', 'in', invoice_line_ids),('parent_state','!=', 'cancel')]) #,('parent_state','=', 'posted')
                        suma_cantidad_facturada = 0
                        suma_unidades_facturadas = 0
                        suma_unidades_por_facturadas = 0
                        ventas_lines_lot_porfacturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lotes.ids),('invoice_status','=','to invoice')])
                        for lin in ventas_lines_lot_porfacturadas:
                            suma_unidades_por_facturadas += lin.qty_delivered
                        for invoice_lin in invoice_line_ids:
                            if invoice_lin.parent_state == 'posted':
                                suma_cantidad_facturada += invoice_lin.credit
                                suma_unidades_facturadas += invoice_lin.quantity
                            else:
                                suma_unidades_por_facturadas += invoice_lin.quantity
                        if  suma_unidades_facturadas > 0:   
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': suma_unidades_facturadas,
                                'precio_prom': (suma_cantidad_facturada/suma_unidades_facturadas),
                                'total': suma_cantidad_facturada
                                }
                            tb_ventas.append(data_line)
                        if suma_unidades_por_facturadas > 0:
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': suma_unidades_por_facturadas,
                                'precio_prom': line.pending_invoice_price,
                                'total': (suma_unidades_por_facturadas*line.pending_invoice_price)
                                }
                            tb_porfacturar.append(data_line)
                        if stock > 0:
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': stock,
                                'precio_prom': line.current_stock_price,
                                'total': (stock*line.current_stock_price)
                                }
                            tb_stock.append(data_line)
                        if scrap_qty > 0:
                            data_line = {
                                'product': line.product_id.display_name,
                                'cajas': scrap_qty,
                                }
                            tb_scrap.append(data_line)


                        #tabla de ventas final    


                        display_name = line.product_id.display_name.replace(
                            ")", "").split("(")
                        variant = len(display_name) > 1 and display_name[1]
                        i += 1
                        sheet.write(i, 0, '', light_box)
                        sheet.write(i, 1, line.product_id.name, light_box)
                        sheet.write(i, 2, variant, light_box)
                        sheet.write(i, 3, line.box_rec, light_box)
                        sheet.write(i, 4, line.price_unit, light_box_currency) #buscar precio original
                        sheet.write(i, 5, "=d{}*e{}".format(str(i+1), str(i+1)), light_box_currency)
                        #sheet.write(i, 6, "", light_box_currency)
                        #sheet.write(i, 7, "", light_box_currency)
                        #sheet.write(i, 8, "", light_box_currency)
                        #sheet.write(i, 9, "", light_box_currency)
                        #sheet.write(i, 10, "=f{}*k{}".format(str(i+1), str(j)), light_box_currency)
                        sheet.write(i, 6, "=f{}".format(str(i+1)), light_box_currency)
                        final_i = i
                    for jj in range(9-(final_i - inicio_i)):
                        i += 1
                        sheet.write(i, 0, '', light_box)
                        sheet.write(i, 1, '', light_box)
                        sheet.write(i, 2, '', light_box)
                        sheet.write(i, 3, '', light_box)
                        sheet.write(i, 4, '', light_box)
                        sheet.write(i, 5, '', light_box)
                        sheet.write(i, 6, '', light_box)
                        #sheet.write(i, 7, '', light_box)
                        #sheet.write(i, 8, '', light_box)
                        #sheet.write(i, 9, '', light_box)
                        #sheet.write(i, 10, '', light_box)
                        #sheet.write(i, 11, '', light_box)
                        sumador = sumador +3

                    
                    #pintar tabla de ventas
                    tb_contador = 11
                    if len(tb_ventas) > 0:
                        sheet.write(tabla_ventas_inicial, tb_contador, 'Ventas', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+2, 'Precio', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+3, 'Total', report_format_gray)
                        contador = tabla_ventas_inicial + 1
                        for linea in tb_ventas:
                            sheet.write(contador, tb_contador, linea['product'], light_box)
                            sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
                            sheet.write(contador, tb_contador+2, linea['precio_prom'], light_box_currency)
                            sheet.write(contador, tb_contador+3, linea['total'], light_box_currency)
                            contador = contador + 1
                        tb_contador += 5

                    if len(tb_porfacturar) > 0:
                        sheet.write(tabla_ventas_inicial, tb_contador, 'Por Facturar', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+2, 'Precio', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+3, 'Total', report_format_gray)
                        contador = tabla_ventas_inicial + 1
                        for linea in tb_porfacturar:
                            sheet.write(contador, tb_contador, linea['product'], light_box)
                            sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
                            sheet.write(contador, tb_contador+2, linea['precio_prom'], light_box_currency)
                            sheet.write(contador, tb_contador+3, linea['total'], light_box_currency)
                            contador = contador + 1
                        tb_contador += 5

                    if len(tb_stock) > 0:
                        sheet.write(tabla_ventas_inicial, tb_contador, 'Stock', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+2, 'Precio', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+3, 'Total', report_format_gray)
                        contador = tabla_ventas_inicial + 1
                        for linea in tb_stock:
                            sheet.write(contador, tb_contador, linea['product'], light_box)
                            sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
                            sheet.write(contador, tb_contador+2, linea['precio_prom'], light_box_currency)
                            sheet.write(contador, tb_contador+3, linea['total'], light_box_currency)
                            contador = contador + 1
                        tb_contador += 5
                    
                    if len(tb_scrap) > 0:
                        sheet.write(tabla_ventas_inicial, tb_contador, 'Scrap', report_format_gray)
                        sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
                        contador = tabla_ventas_inicial + 1
                        for linea in tb_scrap:
                            sheet.write(contador, tb_contador, linea['product'], light_box)
                            sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
                            contador = contador + 1
                        tb_contador += 5

                    #finaliza tabla de ventas
                    
                    
                    sheet.write(i+1, 0, '', light_box)
                    sheet.write(i+1, 1, '', light_box)
                    sheet.write(i+1, 2, '', light_box)
                    sheet.write(i+1, 3, "", light_box)
                    sheet.write(i+1, 4, '', light_box)
                    sheet.write(i+1, 5, "=sum(f{}:f{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                    #sheet.write(i+1, 6, settlement_id.freight_total, light_box_currency)
                    #sheet.write(i+1, 7, settlement_id.aduana_total, light_box_currency)
                    #sheet.write(i+1, 8, settlement_id.storage_total + settlement_id.maneuvers_total , light_box_currency)
                    #sheet.write(i+1, 9, settlement_id.boxes , light_box_currency)
                    #sheet.write(i+1, 10, "=sum(k{}:k{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
                    sheet.write(i+1, 6, "=sum(g{}:g{})".format(str(inicio_i), str(i+1)), light_box_currency)
                    sheet.write(liquidacion_ubicacion, 9, "=g{}".format(str(i+2)), travels_middle_right)
                    liquidaciones.append(liquidacion_ubicacion)
                    sheet.write(liquidacion_ubicacion+9, 9, "=(j{}+j{}+j{})-sum(j{}:j{})".format(str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion),str(liquidacion_ubicacion+1),str(liquidacion_ubicacion+9)), travels_middle_right)
                    sheet.write(liquidacion_ubicacion+11, 9, "=(j{}/(j{}+j{}+j{}))".format(str(liquidacion_ubicacion+10),str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion)), light_box_percentage)
                    i += 7

                    total_total += sale_update
                    total_porfacturar += exists_st.pending_invoice_value
                    total_stock += exists_st.stock_value
                    total_freight_in += freight_in_update
                    total_aduana_total += aduana_usa_update + aduana_mex_update
                    total_maneuvers_total += maneuvers_update
                    total_adjustment += adjustment_update
                    total_storage += storage_update
                    total_freight_out += freight_out_update
                    total_utility += settlement_id.utility
                    total_boxes += boxes_update

                    total_utility_percentage = float_round(settlement_id.utility_percentage, precision_digits=2)
                    utility_per_qty += 1
                    sumador = sumador + 15

                #aqui va a terminar el if de tipo de liquidacion
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
                sheet.write(i+1, 9, '', light_header_bottom)
                sheet.write(i+2, 0, 'Sin liquidación', report_format)
                i += 3

    # def crear_tabla_ziquierda(self, workbook, po, sheet, i, settlement_id):
    #     travels = workbook.add_format({
    #         'font_color' : 'black',
    #         'font_size'  : '14',  
    #         'font_name'  : 'arial',
    #         'align'      : 'left',
    #         'bold'       : True
    #     })
    #     name = workbook.add_format({
    #         'font_color' : 'black',
    #         'font_size'  : '14',  
    #         'font_name'  : 'arial',
    #         'align'      : 'right',
    #         'bold'       : True
    #     })
    #     travels_title_top_left = workbook.add_format({
    #         'font_color' : 'black', 
    #         'font_size'  : '14', 
    #         'font_name'  : 'arial', 
    #         'align'      : 'left', 
    #         'top'        : 2, 
    #         'left'       : 2,
    #         'bold'       : True
    #     })
    #     travels_middle_left = workbook.add_format({
    #         'font_color' : 'black',
    #         'font_size'  : '14', 
    #         'font_name'  : 'arial', 
    #         'align'      : 'left', 
    #         'left'       : 2,
    #         'bold'       : True
    #     })
    #     travels_bottom_left = workbook.add_format({
    #         'font_color' : 'black',
    #         'font_size'  : '14', 
    #         'font_name'  : 'arial', 
    #         'align'      : 'left', 
    #         'left'       : 2,
    #         'bottom'     : 2,
    #         'bold'       : True
    #     })
    #     travels_middle_left_red = workbook.add_format({
    #         'font_color' : 'white',
    #         'font_size'  : '14', 
    #         'font_name'  : 'arial', 
    #         'align'      : 'left', 
    #         'left'       : 2, 
    #         'bg_color'   : 'red',
    #         'bold'       : True
    #     })
    #     travels_title_top_right = workbook.add_format({
    #         'font_color' : 'black', 
    #         'font_size'  : '14', 
    #         'font_name'  : 'arial', 
    #         'align'      : 'right', 
    #         'top'        : 2, 
    #         'right'      : 2,
    #         'bold'       : True,
    #         'num_format': '#,##0.00'
    #     })
    #     travels_middle_right = workbook.add_format({
    #         'font_color' : 'black',
    #         'font_size'  : '14', 
    #         'font_name'  : 'arial', 
    #         'align'      : 'right', 
    #         'right'      : 2,
    #         'bold'       : True,
    #         'num_format': '#,##0.00'
    #     })
    #     travels_middle_right_red = workbook.add_format({
    #         'font_color' : 'white',
    #         'font_size'  : '14', 
    #         'font_name'  : 'arial', 
    #         'align'      : 'right', 
    #         'right'      : 2, 
    #         'bg_color'   : 'red',
    #         'bold'       : True,
    #         'num_format': '#,##0.00'
    #     })
    #     travels_bottom_right = workbook.add_format({
    #         'font_color' : 'black',
    #         'font_size'  : '14', 
    #         'font_name'  : 'arial', 
    #         'align'      : 'right', 
    #         'right'      : 2,
    #         'bottom'     : 2,
    #         'bold'       : True,
    #         'num_format': '#,##0.00'
    #     })
    #     report_format = workbook.add_format({
    #         'font_size'  : '10',
    #         'font_name'  : 'arial',
    #         'border'     : 2,
    #         'bold'       : True,
    #         'align'      : 'center',
    #     })
    #     light_header_top = workbook.add_format({
    #         'font_size'  : '14',
    #         'font_name'  : 'arial',
    #         'top'        : 2,
    #         'right'      : 1,
    #         'left'       : 1,
    #         'bottom'     : 1,
    #         'align'      : 'center',
    #     })
    #     light_header_bottom = workbook.add_format({
    #         'font_size'  : '14',
    #         'font_name'  : 'arial',
    #         'bottom'     : 2,
    #         'top'        : 1,
    #         'right'      : 1,
    #         'left'       : 1,
    #         'align'      : 'center',
    #     })
    #     bold_header = workbook.add_format({
    #         'font_size'  : '14', 
    #         'font_name'  : 'arial',
    #         'bottom'     : 2,
    #         'bold'       : True,
    #         'align'      : 'center',
    #     })
    #     light_box = workbook.add_format({
    #         'font_size'  : '14', 
    #         'font_name'  : 'arial',
    #         'bottom'     : 1,
    #         'top'        : 1, 
    #         'right'      : 1,
    #         'left'       : 1,
    #         'align'      : 'center',
    #     })
    #     light_box_currency = workbook.add_format({
    #         'font_size'  : '14', 
    #         'font_name'  : 'arial',
    #         'bottom'     : 1,
    #         'top'        : 1, 
    #         'right'      : 1,
    #         'left'       : 1,
    #         'align'      : 'center',
    #     })
    #     report_format_gray = workbook.add_format({
    #         'font_size'  : '10',
    #         'font_name'  : 'arial',
    #         'border'     : 2,
    #         'bold'       : True,
    #         'align'      : 'center',
    #         'bg_color'   : 'gray',
    #     })
        
    #     exists_st = self.env['sale.settlements'].search([('order_id', '=', po.id)], limit=1)
    #     if exists_st.price_type == 'open':
    #         #codigo para determinar datos actualizables
    #         po_product_ids = [line.product_id for line in po.order_line]
    #         fecha = po.date_order
    #         picking_ids = po.picking_ids.filtered(lambda picking: picking.state == 'done') # Se obtinenen pickings de la orden de compra
    #         lot_ids = self.env["stock.production.lot"]
    #         for sml in picking_ids.move_line_ids:
    #             lot_ids += sml.lot_id
    #         analytic_tag_ids = self.env['account.analytic.tag']
    #         for lot in lot_ids:
    #             tag = lot.analytic_tag_ids.filtered(lambda tag: len(tag.name)>5)
    #             if not tag in analytic_tag_ids:
    #                 analytic_tag_ids += tag
    #         move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
    #         sales_lines = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.move_id.state == 'posted')
    #         sales_ajust_lines = move_line_ids.filtered(lambda line: line.account_id.id in (1377, 1379) and line.move_id.state == 'posted')
    #         freight_in = move_line_ids.filtered(lambda line: line.account_id.id == 1387 and line.move_id.state == 'posted')
    #         freight_out = move_line_ids.filtered(lambda line: line.account_id.id == 1394 and line.move_id.state == 'posted')
    #         maneuvers = move_line_ids.filtered(lambda line: line.account_id.id == 1390 and line.move_id.state == 'posted')
    #         storage = move_line_ids.filtered(lambda line: line.account_id.id == 1395 and line.move_id.state == 'posted')
    #         aduana_usa = move_line_ids.filtered(lambda line: line.account_id.id == 1393 and line.move_id.state == 'posted')
    #         aduana_mex = move_line_ids.filtered(lambda line: line.account_id.id == 1392 and line.move_id.state == 'posted')#[]1392
    #         adjustment = move_line_ids.filtered(lambda line: line.account_id.id == 1378 and line.move_id.state == 'posted')
    #         boxes = move_line_ids.filtered(lambda line: line.account_id.id == 1509 and line.move_id.state == 'posted')
    #         sale_update = sum([sale.price_subtotal for sale in sales_lines])
    #         sale_ajust_update = sum([sale.price_subtotal for sale in sales_ajust_lines])
    #         sale_update = sale_update - sale_ajust_update
    #         freight_in_update = sum([accline.price_subtotal for accline in freight_in])
    #         freight_out_update = sum([accline.price_subtotal for accline in freight_out])
    #         maneuvers_update = sum([accline.price_subtotal for accline in maneuvers])
    #         storage_update = sum([accline.price_subtotal for accline in storage])
    #         aduana_usa_update = sum([accline.price_subtotal for accline in aduana_usa])
    #         aduana_mex_update = sum([accline.price_subtotal for accline in aduana_mex])
    #         boxes_update = sum([accline.debit for accline in boxes])
    #         adjustment_update = sum([accline.price_subtotal for accline in adjustment])

    #         exists_st.calcular_update()

    #         #termina datos actualizables

    #         #aqui poner el if para open close
    #         settlement_id = exists_st
    #         lang = self.env.user.lang
    #         lang_id = self.env['res.lang'].search([('code', '=', lang)])
    #         datestring = fields.Date.from_string(str(po.date_order)).strftime(lang_id.date_format)
    #         #inicia tabla liquidacion izquiersa
    #         sheet.write(i, 0, 'NOTA', report_format_gray)
    #         sheet.write(i, 1, 'VIAJE', report_format_gray)
            
    #         sheet.write(i+1, 0, settlement_id.note, report_format_gray)
    #         sheet.write(i+1, 1, settlement_id.journey, report_format_gray)

    #         sheet.write(i+2, 0, '', report_format)
    #         sheet.write(i+2, 1, '', report_format)
    #         sheet.write(i+2, 2, '', light_header_top)
    #         # sheet.write(6, 3, 'Cajas', light_header_top)
    #         sheet.write(i+2, 3, 'Cajas', light_header_top)
    #         sheet.write(i+2, 4, '$', light_header_top)
    #         sheet.write(i+2, 5, '$', light_header_top)
    #         sheet.write(i+2, 6, '(-)Flete', light_header_top)
    #         sheet.write(i+2, 7, 'Aduana', light_header_top)
    #         sheet.write(i+2, 8, 'In&Out', light_header_top)
    #         sheet.write(i+2, 9, 'Boxes', light_header_top)
    #         sheet.write(i+2, 10, '(-)Comision', light_header_top)
    #         sheet.write(i+2, 11, '', light_header_top)
            
    #         sheet.write(i+3, 0, 'Fecha', bold_header)
    #         sheet.write(i+3, 1, 'Producto', light_header_bottom)
    #         sheet.write(i+3, 2, 'Medida', light_header_bottom)
    #         # sheet.write(7, 3, 'Emb.', light_header_bottom)
    #         sheet.write(i+3, 3, 'Rec.', light_header_bottom)
    #         sheet.write(i+3, 4, 'P.Unit.', light_header_bottom)
    #         sheet.write(i+3, 5, 'Importe.', light_header_bottom)
    #         sheet.write(i+3, 6, '', light_header_bottom)
    #         sheet.write(i+3, 7, '', light_header_bottom)
    #         sheet.write(i+3, 8, '', light_header_bottom)
    #         sheet.write(i+3, 9, '', light_header_bottom)
    #         sheet.write(
    #             i+3, 10,
    #             "%d %%" % settlement_id.commission_percentage,
    #             light_header_bottom)
    #         sheet.write(i+3, 11, 'Total', light_header_bottom)

    #         sheet.write(i+5, 0, datestring, light_box)
            
    #         exists_st.actualizacion = True
    #         tabla_ventas_inicial =  i + 5
    #         liquidacion_ubicacion = i + 4
    #         i += 5
    #         j = i - 1
    #         inicio_i = i
    #         final_i = i
    #         sheet.write(i - 1, 11, (-settlement_id.freight_total-settlement_id.aduana_total-settlement_id.storage_total-settlement_id.maneuvers_total-settlement_id.boxes), light_box_currency)
    #         #activar variables para cuadro vde ventas
    #         tb_ventas = []
    #         tb_porfacturar = []
    #         tb_stock = []
    #         tb_scrap = []

    #         for line in settlement_id.settlements_line_ids:
    #             #tabla de ventas inicio
    #             line_lotes =  self.env['stock.production.lot'].search([('id', 'in', lot_ids.ids),('product_id', '=', line.product_id.id)])
    #             line_lotes += self.env['stock.production.lot'].search([('parent_lod_id', 'in', line_lotes.ids)])
    #             quant_obj = self.env["stock.quant"] 
    #             location_id = self.env["stock.location"].search([('usage', '=', 'internal')])
    #             quants1 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', location_id.ids)])
    #             scrap_loc_id = self.env["stock.location"].search([('scrap_location', '=', True)])
    #             quants2 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', scrap_loc_id.ids)])
    #             stock = sum([q.quantity for q in quants1])
    #             scrap_qty = sum([q.quantity for q in quants2])
    #             ventas_lines_lot_facturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lotes.ids),('invoice_status','=','invoiced')])
    #             invoice_line_ids = []
    #             for lin in ventas_lines_lot_facturadas:
    #                 invoice_line_ids.extend(lin.invoice_lines.ids)
    #             invoice_line_ids = self.env['account.move.line'].search([('id', 'in', invoice_line_ids),('parent_state','!=', 'cancel')]) #,('parent_state','=', 'posted')
    #             suma_cantidad_facturada = 0
    #             suma_unidades_facturadas = 0
    #             suma_unidades_por_facturadas = 0
    #             ventas_lines_lot_porfacturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lotes.ids),('invoice_status','=','to invoice')])
    #             for lin in ventas_lines_lot_porfacturadas:
    #                 suma_unidades_por_facturadas += lin.qty_delivered
    #             for invoice_lin in invoice_line_ids:
    #                 if invoice_lin.parent_state == 'posted':
    #                     suma_cantidad_facturada += invoice_lin.credit
    #                     suma_unidades_facturadas += invoice_lin.quantity
    #                 else:
    #                     suma_unidades_por_facturadas += invoice_lin.quantity
    #             if  suma_unidades_facturadas > 0:   
    #                 data_line = {
    #                     'product': line.product_id.display_name,
    #                     'cajas': suma_unidades_facturadas,
    #                     'precio_prom': (suma_cantidad_facturada/suma_unidades_facturadas),
    #                     'total': suma_cantidad_facturada
    #                     }
    #                 tb_ventas.append(data_line)
    #             if suma_unidades_por_facturadas > 0:
    #                 data_line = {
    #                     'product': line.product_id.display_name,
    #                     'cajas': suma_unidades_por_facturadas,
    #                     'precio_prom': line.pending_invoice_price,
    #                     'total': (suma_unidades_por_facturadas*line.pending_invoice_price)
    #                     }
    #                 tb_porfacturar.append(data_line)
    #             if stock > 0:
    #                 data_line = {
    #                     'product': line.product_id.display_name,
    #                     'cajas': stock,
    #                     'precio_prom': line.current_stock_price,
    #                     'total': (stock*line.current_stock_price)
    #                     }
    #                 tb_stock.append(data_line)
    #             if scrap_qty > 0:
    #                 data_line = {
    #                     'product': line.product_id.display_name,
    #                     'cajas': scrap_qty,
    #                     }
    #                 tb_scrap.append(data_line)


    #             #tabla de ventas final


    #             display_name = line.product_id.display_name.replace(
    #                 ")", "").split("(")
    #             variant = len(display_name) > 1 and display_name[1]
    #             i += 1
    #             sheet.write(i, 0, '', light_box)
    #             sheet.write(i, 1, line.product_id.name, light_box)
    #             sheet.write(i, 2, variant, light_box)
    #             sheet.write(i, 3, line.box_rec, light_box)
    #             sheet.write(i, 4, line.price_unit, light_box_currency)
    #             sheet.write(i, 5, "=d{}*e{}".format(str(i+1), str(i+1)), light_box_currency)
    #             sheet.write(i, 6, "", light_box_currency)
    #             sheet.write(i, 7, "", light_box_currency)
    #             sheet.write(i, 8, "", light_box_currency)
    #             sheet.write(i, 9, "", light_box_currency)
    #             sheet.write(i, 10, "=f{}*k{}".format(str(i+1), str(j)), light_box_currency)
    #             sheet.write(i, 11, "=f{}-k{}".format(str(i+1), str(i+1)), light_box_currency)
    #             final_i = i
    #         for jj in range(9-(final_i - inicio_i)):
    #             i += 1
    #             sheet.write(i, 0, '', light_box)
    #             sheet.write(i, 1, '', light_box)
    #             sheet.write(i, 2, '', light_box)
    #             sheet.write(i, 3, '', light_box)
    #             sheet.write(i, 4, '', light_box)
    #             sheet.write(i, 5, '', light_box)
    #             sheet.write(i, 6, '', light_box)
    #             sheet.write(i, 7, '', light_box)
    #             sheet.write(i, 8, '', light_box)
    #             sheet.write(i, 9, '', light_box)
    #             sheet.write(i, 10, '', light_box)
    #             sheet.write(i, 11, '', light_box)
    #             sumador = sumador +3
            
            
            
    #         sheet.write(i+1, 0, '', light_box)
    #         sheet.write(i+1, 1, '', light_box)
    #         sheet.write(i+1, 2, '', light_box)
    #         sheet.write(i+1, 3, "", light_box)
    #         sheet.write(i+1, 4, '', light_box)
    #         sheet.write(i+1, 5, "=sum(f{}:f{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
    #         sheet.write(i+1, 6, settlement_id.freight_total, light_box_currency)
    #         sheet.write(i+1, 7, settlement_id.aduana_total, light_box_currency)
    #         sheet.write(i+1, 8, settlement_id.storage_total + settlement_id.maneuvers_total , light_box_currency)
    #         sheet.write(i+1, 9, settlement_id.boxes , light_box_currency)
    #         sheet.write(i+1, 10, "=sum(k{}:k{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
    #         sheet.write(i+1, 11, "=sum(l{}:l{})".format(str(inicio_i), str(i+1)), light_box_currency)
    #         sheet.write(liquidacion_ubicacion, 14, "=l{}".format(str(i+2)), travels_middle_right)
    #         liquidaciones.append(liquidacion_ubicacion)
    #         sheet.write(liquidacion_ubicacion+9, 14, "=(o{}+o{}+o{})-sum(o{}:o{})".format(str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion),str(liquidacion_ubicacion+1),str(liquidacion_ubicacion+9)), travels_middle_right)
    #         sheet.write(liquidacion_ubicacion+11, 14, "=(o{}/(o{}+o{}+o{}))".format(str(liquidacion_ubicacion+10),str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion)), travels_middle_right)
    #         i += 7

    #         total_total += sale_update
    #         total_porfacturar += exists_st.pending_invoice_value
    #         total_stock += exists_st.stock_value
    #         total_freight_in += freight_in_update
    #         total_aduana_total += aduana_usa_update + aduana_mex_update
    #         total_maneuvers_total += maneuvers_update
    #         total_adjustment += adjustment_update
    #         total_storage += storage_update
    #         total_freight_out += freight_out_update
    #         total_utility += settlement_id.utility
    #         total_boxes += boxes_update

    #         total_utility_percentage = float_round(settlement_id.utility_percentage, precision_digits=2)
    #         utility_per_qty += 1
    #         sumador = sumador + 15
    #     else:
    #         po_product_ids = [line.product_id for line in po.order_line]
    #         fecha = po.date_order
    #         picking_ids = po.picking_ids.filtered(lambda picking: picking.state == 'done') # Se obtinenen pickings de la orden de compra
    #         lot_ids = self.env["stock.production.lot"]
    #         for sml in picking_ids.move_line_ids:
    #             lot_ids += sml.lot_id
    #         analytic_tag_ids = self.env['account.analytic.tag']
    #         for lot in lot_ids:
    #             tag = lot.analytic_tag_ids.filtered(lambda tag: len(tag.name)>5)
    #             if not tag in analytic_tag_ids:
    #                 analytic_tag_ids += tag
    #         move_line_ids = self.env['account.move.line'].search([('analytic_tag_ids', 'in', analytic_tag_ids.ids), ('move_id.state', '=', 'posted')])
    #         sales_lines = move_line_ids.filtered(lambda line: line.account_id.id == 38 and line.move_id.state == 'posted')
    #         sales_ajust_lines = move_line_ids.filtered(lambda line: line.account_id.id in (1377, 1379) and line.move_id.state == 'posted')
    #         freight_in = move_line_ids.filtered(lambda line: line.account_id.id == 1387 and line.move_id.state == 'posted')
    #         freight_out = move_line_ids.filtered(lambda line: line.account_id.id == 1394 and line.move_id.state == 'posted')
    #         maneuvers = move_line_ids.filtered(lambda line: line.account_id.id == 1390 and line.move_id.state == 'posted')
    #         storage = move_line_ids.filtered(lambda line: line.account_id.id == 1395 and line.move_id.state == 'posted')
    #         aduana_usa = move_line_ids.filtered(lambda line: line.account_id.id == 1393 and line.move_id.state == 'posted')
    #         aduana_mex = move_line_ids.filtered(lambda line: line.account_id.id == 1392 and line.move_id.state == 'posted')#[]1392
    #         adjustment = move_line_ids.filtered(lambda line: line.account_id.id == 1378 and line.move_id.state == 'posted')
    #         boxes = move_line_ids.filtered(lambda line: line.account_id.id == 1509 and line.move_id.state == 'posted')
    #         sale_update = sum([sale.price_subtotal for sale in sales_lines])
    #         sale_ajust_update = sum([sale.price_subtotal for sale in sales_ajust_lines])
    #         sale_update = sale_update - sale_ajust_update
    #         freight_in_update = sum([accline.price_subtotal for accline in freight_in])
    #         freight_out_update = sum([accline.price_subtotal for accline in freight_out])
    #         maneuvers_update = sum([accline.price_subtotal for accline in maneuvers])
    #         storage_update = sum([accline.price_subtotal for accline in storage])
    #         aduana_usa_update = sum([accline.price_subtotal for accline in aduana_usa])
    #         aduana_mex_update = sum([accline.price_subtotal for accline in aduana_mex])
    #         boxes_update = sum([accline.debit for accline in boxes])
    #         adjustment_update = sum([accline.price_subtotal for accline in adjustment])

    #         exists_st.calcular_update()

    #         settlement_id = exists_st
    #         lang = self.env.user.lang
    #         lang_id = self.env['res.lang'].search([('code', '=', lang)])
    #         datestring = fields.Date.from_string(str(po.date_order)).strftime(lang_id.date_format)
    #         sheet.write(i, 0, 'NOTA', report_format_gray)
    #         sheet.write(i, 1, 'VIAJE', report_format_gray)
            
    #         sheet.write(i+1, 0, settlement_id.note, report_format_gray)
    #         sheet.write(i+1, 1, settlement_id.journey, report_format_gray)

    #         sheet.write(i+2, 0, '', report_format)
    #         sheet.write(i+2, 1, '', report_format)
    #         sheet.write(i+2, 2, '', light_header_top)
    #         # sheet.write(6, 3, 'Cajas', light_header_top)
    #         sheet.write(i+2, 3, 'Cajas', light_header_top)
    #         sheet.write(i+2, 4, '$', light_header_top)
    #         sheet.write(i+2, 5, '$', light_header_top)
    #         #sheet.write(i+2, 6, '(-)Flete', light_header_top)
    #         #sheet.write(i+2, 7, 'Aduana', light_header_top)
    #         #sheet.write(i+2, 8, 'In&Out', light_header_top)
    #         #sheet.write(i+2, 9, 'Boxes', light_header_top)
    #         #sheet.write(i+2, 10, '(-)Comision', light_header_top)
    #         sheet.write(i+2, 6, '', light_header_top)
            
    #         sheet.write(i+3, 0, 'Fecha', bold_header)
    #         sheet.write(i+3, 1, 'Producto', light_header_bottom)
    #         sheet.write(i+3, 2, 'Medida', light_header_bottom)
    #         # sheet.write(7, 3, 'Emb.', light_header_bottom)
    #         sheet.write(i+3, 3, 'Rec.', light_header_bottom)
    #         sheet.write(i+3, 4, 'P.Unit.', light_header_bottom)
    #         sheet.write(i+3, 5, 'Importe.', light_header_bottom)
    #         #sheet.write(i+3, 6, '', light_header_bottom)
    #         #sheet.write(i+3, 7, '', light_header_bottom)
    #         #sheet.write(i+3, 8, '', light_header_bottom)
    #         #sheet.write(i+3, 9, '', light_header_bottom)
    #         #sheet.write(i+3, 10,"%d %%" % settlement_id.commission_percentage, light_header_bottom)
    #         sheet.write(i+3, 6, 'Total', light_header_bottom)

    #         sheet.write(i+5, 0, datestring, light_box)
            
    #         if len(procesar_object)> 1 or exists_st.actualizacion == True:
    #             sheet.write(i, 8, 'Viaje', travels)
    #             sheet.write(i + 1, 8, 'VENTAS', travels_title_top_left)
    #             sheet.write(i + 2, 8, 'POR FACTURAR', travels_title_top_left)
    #             sheet.write(i + 3, 8, 'STOCK', travels_title_top_left)
    #             sheet.write(i + 4, 8, 'LIQUIDACIONES', travels_middle_left)
    #             sheet.write(i + 5, 8, 'Freight In', travels_middle_left)
    #             sheet.write(i + 6, 8, 'Aduana', travels_middle_left)
    #             sheet.write(i + 7, 8, 'MANIOBRAS', travels_middle_left_red)
    #             sheet.write(i + 8, 8, 'AJUSTE', travels_middle_left_red)
    #             sheet.write(i + 9, 8, 'STORAGE', travels_middle_left_red)
    #             sheet.write(i + 10, 8, 'FREIGHT OUT', travels_middle_left_red)
    #             sheet.write(i + 11, 8, 'CAJAS', travels_middle_left_red)
    #             sheet.write(i + 13, 8, 'UTILIDAD', travels_middle_left)
    #             sheet.write(i, 9, po.name, name)
    #             sheet.write(i + 1, 9, sale_update, travels_title_top_right)
    #             sheet.write(i + 2, 9, exists_st.pending_invoice_value, travels_middle_right)
    #             sheet.write(i + 3, 9, exists_st.stock_value, travels_middle_right)
    #             sheet.write(i + 5, 9, freight_in_update, travels_middle_right)
    #             sheet.write(i + 6, 9, aduana_usa_update+aduana_mex_update, travels_middle_right)
    #             sheet.write(i + 7, 9, maneuvers_update, travels_middle_right_red)
    #             sheet.write(i + 8, 9, adjustment_update, travels_middle_right_red)
    #             sheet.write(i + 9, 9, storage_update, travels_middle_right_red)
    #             sheet.write(i + 10, 9, freight_out_update, travels_middle_right_red)
    #             sheet.write(i + 11, 9, boxes_update, travels_middle_right_red)
    #             sheet.write(i + 13, 9, settlement_id.utility, travels_middle_right)
    #             sheet.write(i + 15, 9, str(float_round(settlement_id.utility_percentage, precision_digits=2)) + "%", travels_bottom_right)
    #             #sheet.write(i + 2, 13, '', travels_middle_left)
    #             #sheet.write(i + 3, 13, '', travels_middle_left)
    #             #sheet.write(i + 11, 13, '', travels_middle_left)
    #             sheet.write(i + 12, 8, '', travels_middle_left)
    #             sheet.write(i + 14, 8, '', travels_middle_left)
    #             #sheet.write(i + 2, 14, '', travels_middle_right)
    #             #sheet.write(i + 3, 14, '', travels_middle_right)
    #             sheet.write(i + 4, 9, settlement_id.settlement, travels_middle_right)
    #             #sheet.write(i + 11, 14, '', travels_middle_right)
    #             sheet.write(i + 12, 9, '', travels_middle_right)
    #             sheet.write(i + 14, 9, '', travels_middle_right)
    #             sheet.write(i + 15, 8, '', travels_bottom_left)
            
    #         exists_st.actualizacion = True
    #         liquidacion_ubicacion = i + 4
    #         tabla_ventas_inicial =  i + 5
    #         i += 5
    #         j = i - 1
    #         inicio_i = i
    #         final_i = i
    #         #activar variables para cuadro vde ventas
    #         tb_ventas = []
    #         tb_porfacturar = []
    #         tb_stock = []
    #         tb_scrap = []

    #         #sheet.write(i - 1, 11, (-settlement_id.freight_total-settlement_id.aduana_total-settlement_id.storage_total-settlement_id.maneuvers_total-settlement_id.boxes), light_box_currency)
    #         for line in settlement_id.settlements_line_ids:

    #             #tabla de ventas inicio
    #             line_lotes =  self.env['stock.production.lot'].search([('id', 'in', lot_ids.ids),('product_id', '=', line.product_id.id)])
    #             line_lotes += self.env['stock.production.lot'].search([('parent_lod_id', 'in', line_lotes.ids)])
    #             quant_obj = self.env["stock.quant"] 
    #             location_id = self.env["stock.location"].search([('usage', '=', 'internal')])
    #             quants1 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', location_id.ids)])
    #             scrap_loc_id = self.env["stock.location"].search([('scrap_location', '=', True)])
    #             quants2 = quant_obj.search([ ('lot_id', 'in', line_lotes.ids), ('location_id', 'in', scrap_loc_id.ids)])
    #             stock = sum([q.quantity for q in quants1])
    #             scrap_qty = sum([q.quantity for q in quants2])
    #             ventas_lines_lot_facturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lotes.ids),('invoice_status','=','invoiced')])
    #             invoice_line_ids = []
    #             for lin in ventas_lines_lot_facturadas:
    #                 invoice_line_ids.extend(lin.invoice_lines.ids)
    #             invoice_line_ids = self.env['account.move.line'].search([('id', 'in', invoice_line_ids),('parent_state','!=', 'cancel')]) #,('parent_state','=', 'posted')
    #             suma_cantidad_facturada = 0
    #             suma_unidades_facturadas = 0
    #             suma_unidades_por_facturadas = 0
    #             ventas_lines_lot_porfacturadas = self.env['sale.order.line'].search([('lot_id', 'in', line_lotes.ids),('invoice_status','=','to invoice')])
    #             for lin in ventas_lines_lot_porfacturadas:
    #                 suma_unidades_por_facturadas += lin.qty_delivered
    #             for invoice_lin in invoice_line_ids:
    #                 if invoice_lin.parent_state == 'posted':
    #                     suma_cantidad_facturada += invoice_lin.credit
    #                     suma_unidades_facturadas += invoice_lin.quantity
    #                 else:
    #                     suma_unidades_por_facturadas += invoice_lin.quantity
    #             if  suma_unidades_facturadas > 0:   
    #                 data_line = {
    #                     'product': line.product_id.display_name,
    #                     'cajas': suma_unidades_facturadas,
    #                     'precio_prom': (suma_cantidad_facturada/suma_unidades_facturadas),
    #                     'total': suma_cantidad_facturada
    #                     }
    #                 tb_ventas.append(data_line)
    #             if suma_unidades_por_facturadas > 0:
    #                 data_line = {
    #                     'product': line.product_id.display_name,
    #                     'cajas': suma_unidades_por_facturadas,
    #                     'precio_prom': line.pending_invoice_price,
    #                     'total': (suma_unidades_por_facturadas*line.pending_invoice_price)
    #                     }
    #                 tb_porfacturar.append(data_line)
    #             if stock > 0:
    #                 data_line = {
    #                     'product': line.product_id.display_name,
    #                     'cajas': stock,
    #                     'precio_prom': line.current_stock_price,
    #                     'total': (stock*line.current_stock_price)
    #                     }
    #                 tb_stock.append(data_line)
    #             if scrap_qty > 0:
    #                 data_line = {
    #                     'product': line.product_id.display_name,
    #                     'cajas': scrap_qty,
    #                     }
    #                 tb_scrap.append(data_line)


    #             #tabla de ventas final    


    #             display_name = line.product_id.display_name.replace(
    #                 ")", "").split("(")
    #             variant = len(display_name) > 1 and display_name[1]
    #             i += 1
    #             sheet.write(i, 0, '', light_box)
    #             sheet.write(i, 1, line.product_id.name, light_box)
    #             sheet.write(i, 2, variant, light_box)
    #             sheet.write(i, 3, line.box_rec, light_box)
    #             sheet.write(i, 4, line.price_unit, light_box_currency) #buscar precio original
    #             sheet.write(i, 5, "=d{}*e{}".format(str(i+1), str(i+1)), light_box_currency)
    #             #sheet.write(i, 6, "", light_box_currency)
    #             #sheet.write(i, 7, "", light_box_currency)
    #             #sheet.write(i, 8, "", light_box_currency)
    #             #sheet.write(i, 9, "", light_box_currency)
    #             #sheet.write(i, 10, "=f{}*k{}".format(str(i+1), str(j)), light_box_currency)
    #             sheet.write(i, 6, "=f{}".format(str(i+1)), light_box_currency)
    #             final_i = i
    #         for jj in range(9-(final_i - inicio_i)):
    #             i += 1
    #             sheet.write(i, 0, '', light_box)
    #             sheet.write(i, 1, '', light_box)
    #             sheet.write(i, 2, '', light_box)
    #             sheet.write(i, 3, '', light_box)
    #             sheet.write(i, 4, '', light_box)
    #             sheet.write(i, 5, '', light_box)
    #             sheet.write(i, 6, '', light_box)
    #             #sheet.write(i, 7, '', light_box)
    #             #sheet.write(i, 8, '', light_box)
    #             #sheet.write(i, 9, '', light_box)
    #             #sheet.write(i, 10, '', light_box)
    #             #sheet.write(i, 11, '', light_box)
    #             sumador = sumador +3

            
    #         #pintar tabla de ventas
    #         tb_contador = 11
    #         if len(tb_ventas) > 0:
    #             sheet.write(tabla_ventas_inicial, tb_contador, 'Ventas', report_format_gray)
    #             sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
    #             sheet.write(tabla_ventas_inicial, tb_contador+2, 'Precio', report_format_gray)
    #             sheet.write(tabla_ventas_inicial, tb_contador+3, 'Total', report_format_gray)
    #             contador = tabla_ventas_inicial + 1
    #             for linea in tb_ventas:
    #                 sheet.write(contador, tb_contador, linea['product'], light_box)
    #                 sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
    #                 sheet.write(contador, tb_contador+2, linea['precio_prom'], light_box_currency)
    #                 sheet.write(contador, tb_contador+3, linea['total'], light_box_currency)
    #                 contador = contador + 1
    #             tb_contador += 5

    #         if len(tb_porfacturar) > 0:
    #             sheet.write(tabla_ventas_inicial, tb_contador, 'Por Facturar', report_format_gray)
    #             sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
    #             sheet.write(tabla_ventas_inicial, tb_contador+2, 'Precio', report_format_gray)
    #             sheet.write(tabla_ventas_inicial, tb_contador+3, 'Total', report_format_gray)
    #             contador = tabla_ventas_inicial + 1
    #             for linea in tb_porfacturar:
    #                 sheet.write(contador, tb_contador, linea['product'], light_box)
    #                 sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
    #                 sheet.write(contador, tb_contador+2, linea['precio_prom'], light_box_currency)
    #                 sheet.write(contador, tb_contador+3, linea['total'], light_box_currency)
    #                 contador = contador + 1
    #             tb_contador += 5

    #         if len(tb_stock) > 0:
    #             sheet.write(tabla_ventas_inicial, tb_contador, 'Stock', report_format_gray)
    #             sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
    #             sheet.write(tabla_ventas_inicial, tb_contador+2, 'Precio', report_format_gray)
    #             sheet.write(tabla_ventas_inicial, tb_contador+3, 'Total', report_format_gray)
    #             contador = tabla_ventas_inicial + 1
    #             for linea in tb_stock:
    #                 sheet.write(contador, tb_contador, linea['product'], light_box)
    #                 sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
    #                 sheet.write(contador, tb_contador+2, linea['precio_prom'], light_box_currency)
    #                 sheet.write(contador, tb_contador+3, linea['total'], light_box_currency)
    #                 contador = contador + 1
    #             tb_contador += 5
            
    #         if len(tb_scrap) > 0:
    #             sheet.write(tabla_ventas_inicial, tb_contador, 'Scrap', report_format_gray)
    #             sheet.write(tabla_ventas_inicial, tb_contador+1, 'Cajas', report_format_gray)
    #             contador = tabla_ventas_inicial + 1
    #             for linea in tb_scrap:
    #                 sheet.write(contador, tb_contador, linea['product'], light_box)
    #                 sheet.write(contador, tb_contador+1, linea['cajas'], light_box)
    #                 contador = contador + 1
    #             tb_contador += 5

    #         #finaliza tabla de ventas
            
            
    #         sheet.write(i+1, 0, '', light_box)
    #         sheet.write(i+1, 1, '', light_box)
    #         sheet.write(i+1, 2, '', light_box)
    #         sheet.write(i+1, 3, "", light_box)
    #         sheet.write(i+1, 4, '', light_box)
    #         sheet.write(i+1, 5, "=sum(f{}:f{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
    #         #sheet.write(i+1, 6, settlement_id.freight_total, light_box_currency)
    #         #sheet.write(i+1, 7, settlement_id.aduana_total, light_box_currency)
    #         #sheet.write(i+1, 8, settlement_id.storage_total + settlement_id.maneuvers_total , light_box_currency)
    #         #sheet.write(i+1, 9, settlement_id.boxes , light_box_currency)
    #         #sheet.write(i+1, 10, "=sum(k{}:k{})".format(str(inicio_i+1), str(i+1)), light_box_currency)
    #         sheet.write(i+1, 6, "=sum(g{}:g{})".format(str(inicio_i), str(i+1)), light_box_currency)
    #         sheet.write(liquidacion_ubicacion, 9, "=g{}".format(str(i+2)), travels_middle_right)
    #         liquidaciones.append(liquidacion_ubicacion)
    #         sheet.write(liquidacion_ubicacion+9, 9, "=(j{}+j{}+j{})-sum(j{}:j{})".format(str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion),str(liquidacion_ubicacion+1),str(liquidacion_ubicacion+9)), travels_middle_right)
    #         sheet.write(liquidacion_ubicacion+11, 9, "=(j{}/(j{}+j{}+j{}))".format(str(liquidacion_ubicacion+10),str(liquidacion_ubicacion-2),str(liquidacion_ubicacion-1),str(liquidacion_ubicacion)), travels_middle_right)
    #         i += 7

    #         total_total += sale_update
    #         total_porfacturar += exists_st.pending_invoice_value
    #         total_stock += exists_st.stock_value
    #         total_freight_in += freight_in_update
    #         total_aduana_total += aduana_usa_update + aduana_mex_update
    #         total_maneuvers_total += maneuvers_update
    #         total_adjustment += adjustment_update
    #         total_storage += storage_update
    #         total_freight_out += freight_out_update
    #         total_utility += settlement_id.utility
    #         total_boxes += boxes_update

    #         total_utility_percentage = float_round(settlement_id.utility_percentage, precision_digits=2)
    #         utility_per_qty += 1
    #         sumador = sumador + 15

    #             #aqui va a terminar el if de tipo de liquidacion

                
        # formula_liquidacion = "=("
        # for liq in liquidaciones:
        #     formula_liquidacion += "+o{}".format(str(liq+1))
        # formula_liquidacion += ")"
        # i += 1
        # if len(procesar_object)>1:
        #     sheet.write(i, 13, 'TOTALES', travels)
        #     sheet.write(i + 1, 13, 'VENTAS', travels_title_top_left)
        #     sheet.write(i + 2, 13, 'POR FACTURAR', travels_middle_left)
        #     sheet.write(i + 3, 13, 'STOCK', travels_middle_left)
        #     sheet.write(i + 4, 13, 'LIQUIDACIONES', travels_middle_left)
        #     sheet.write(i + 5, 13, 'Freight In', travels_middle_left)
        #     sheet.write(i + 6, 13, 'Aduana', travels_middle_left)
        #     sheet.write(i + 7, 13, 'MANIOBRAS', travels_middle_left_red)
        #     sheet.write(i + 8, 13, 'AJUSTE', travels_middle_left_red)
        #     sheet.write(i + 9, 13, 'STORAGE', travels_middle_left_red)
        #     sheet.write(i + 10, 13, 'FREIGHT OUT', travels_middle_left_red)
        #     sheet.write(i + 13, 13, 'UTILIDAD', travels_middle_left)
        #     sheet.write(i + 11, 13, 'CAJAS', travels_middle_left)
        #     sheet.write(i + 1, 14, total_total, travels_title_top_right)
        #     sheet.write(i + 2, 14, total_porfacturar , travels_middle_right)
        #     sheet.write(i + 3, 14, total_stock, travels_middle_right)
        #     sheet.write(i + 4, 14, formula_liquidacion, travels_middle_right)
        #     sheet.write(i + 5, 14, total_freight_in, travels_middle_right)
        #     sheet.write(i + 6, 14, total_aduana_total, travels_middle_right)
        #     sheet.write(i + 7, 14, total_maneuvers_total, travels_middle_right_red)
        #     sheet.write(i + 8, 14, total_adjustment, travels_middle_right_red)
        #     sheet.write(i + 9, 14, total_storage, travels_middle_right_red)
        #     sheet.write(i + 10, 14, total_freight_out , travels_middle_right_red)
        #     sheet.write(i + 11, 14, total_boxes, travels_middle_right_red)
        #     sheet.write(i + 13, 14, "=(o{}+o{}+o{})-sum(o{}:o{})".format(str(i+2),str(i+3),str(i+4),str(i+5),str(i+13)), travels_middle_right)
        #     sheet.write(i + 15, 14, "=(o{}/(o{}+o{}+o{}))".format(str(i+14),str(i+2),str(i+3),str(i+4)), travels_middle_right)

        #     #sheet.write(i + 2, 13, '', travels_middle_left)
        #     #sheet.write(i + 3, 13, '', travels_middle_left)
        #     #sheet.write(i + 11, 1, '', travels_middle_left)
        #     sheet.write(i + 12, 13, '', travels_middle_left)
        #     sheet.write(i + 14, 13, '', travels_middle_left)
        #     #sheet.write(i + 2, 14, '', travels_middle_right)
        #     #sheet.write(i + 3, 14, '', travels_middle_right)
        #     #sheet.write(i + 4, 14, '', travels_middle_right)
        #     #sheet.write(i + 11, 2, '', travels_middle_right)
        #     #sheet.write(i + 12, 14, '', travels_middle_right)
        #     #sheet.write(i + 14, 14, '', travels_middle_right)
        #     #sheet.write(i + 15, 14, '', travels_bottom_left)