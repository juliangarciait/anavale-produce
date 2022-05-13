# -*- coding: utf-8 -*-

{
    'name': "Formato del reporte del lote con código de barras",
    'summary': """
    Se cambia el formato del reporte generado desde el lote, y el dato con el cual se genera el código de barras.
    """, 
    'description': """
    Se cambia el formato del reporte generado desde el lote, y el dato con el cual se genera el código de barras.
    """,
    'author': "Quemari developers",
    'website': "http://www.quemari.com",
    'category': "Inventory",
    'depends': [
        'stock'
    ],
    'data': [
        'report/report_lot_barcode.xml', 

        'views/stock_production_lot_form_inherit_view.xml'
    ]
}