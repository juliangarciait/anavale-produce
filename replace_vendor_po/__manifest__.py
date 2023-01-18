# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Change Vendor in Purchase Order',
    'author': 'Altela Softwares',
    'version': '13.0.2.0.0',
    'summary': 'Change or Replace Vendor in Purchase Order',
    'license': 'OPL-1',
    'sequence': 1,
    'description': """Allows You Changing or Replacing Vendor in Purchase Order, And Push The Update to DO, Invoice & Journal Entries""",
    'category': 'Purchase',
    'website': 'https://www.altela.net',
    'price':'15',
    'currency':'USD',
    'depends': [
        'purchase',
        'stock',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/replace_vendor_po.xml'
    ],
    'images': [
        'static/description/banner.gif',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'pre_init_hook': 'pre_init_check',
}
