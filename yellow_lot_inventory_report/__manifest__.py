# -*- coding: utf-8 -*-

{
    'name': "Color amarillo al lote con base a los alerts",
    'summary': """
    El color del lote en el reporte de inventario cambia a amarillo si han pasado cinco días, tomando como base el alert time
    """,
    'description': """
    El color del lote en el reporte de inventario cambia a amarillo si han pasado cinco días, tomando como base el alert time
    """,
    'author': "Quemari developers",
    'website': "http://www.quemari.com",
    'category': "Inventory",
    'depends': [
        'stock'
    ],
    'data': [
        'views/stock_quant_tree_editable_inherit_view.xml'
    ]

}