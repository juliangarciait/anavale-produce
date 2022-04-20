# -*- coding: utf-8 -*-
{
    'name': "Fecha custom a asiento generado por Picking",

    'summary': """
        Fecha custom a asiento generado por Picking""",

    'description': """
        Fecha custom a asiento generado por Picking
    """,

    'author': "Quemari developers",
    'website': "http://www.quemari.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale_management',
        'stock'
    ],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}