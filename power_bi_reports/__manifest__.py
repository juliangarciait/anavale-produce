# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Power Bi Reports',
    'author': 'Julian Garcia',
    'version': '13.0.1',
    'summary': 'Modulo para administratar cotizaciones de compra',
    'license': 'OPL-1',
    'sequence': 1,
    'description': """Este modulo nos dara herramientas para la administracion y calculo de cotizaciones y oportunidades de compra""",
    'category': 'Purchase',
    'website': '',
    'depends': [
        'purchase',
        'stock',
        'account',
    ],
    'data': [
        #'security/security.xml',
        'security/ir.model.access.csv',
        'views/budget_view.xml'
    ],
    'images': [
        
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
