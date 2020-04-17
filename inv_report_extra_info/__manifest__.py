# -*- coding: utf-8 -*-
###################################################################################
#
#    ITStore
#    Copyright (C) 2019-TODAY ITStore (<http://itstore.odoo.com>).
#    Author: ITStore (<http://itstore.odoo.com>)
#
#    you can modify it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#
###################################################################################
{
    'name': 'Inventory Report Extra Info',
    'version': '13.0.0.1',
    'summary': 'Analyse incoming and outgoing stock related status',
    'category': 'Industries',
    'author': 'ITStore',
    'maintainer': 'ITStore',
    'website': 'http://itstore.odoo.com',
    'support': 'itstore005@gmail.com',
    'depends': [
        'stock', 'sale', 'purchase', 'sale_stock', 'purchase_stock',
    ],
    'data': [
        'views/stock_inventory_view.xml',
        'wizard/view_pickings_wiz.xml',
    ],
    'images': ['static/description/banner.png'],
    'live_test_url': "https://youtu.be/LxxMoPpZrC4",
    'application': True,
    'license': 'LGPL-3',
    'price': 25.00,
    'currency': 'EUR',
}
