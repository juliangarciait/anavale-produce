# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2019 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'NSF Check (Odoo Enterprise)',
    'version': '13.0.0.1',
    'category': 'Accounting',
    'summary': "This Module provide check bounce and reverse Payment functionality.",
    'description': """
        This Module provide check bounce and reverse Payment functionality."
    """,
    'website': 'https://www.bistasolutions.com',
    'author': 'Bista Solutions',
    'price': 25,
    'currency': 'USD',
    'license': 'OPL-1',
    'images': ['static/description/NSFGIF.gif', 'static/description/NSFGIF2.gif',
               'static/description/icon.png', 'static/description/1.png', 'static/description/2.png',
               'static/description/3.png', 'static/description/4.png', 'static/description/5.png',],
    'depends': ['account'],
    'data': [
            'views/payment_view.xml',
            'data/product_data.xml',
            'wizard/check_bounce_view.xml',
    ],
    'installable': True,
    'application': False,
}
