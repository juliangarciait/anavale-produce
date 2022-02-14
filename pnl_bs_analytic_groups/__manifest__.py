# -*- coding: utf-8 -*-
###############################################################################
#
#   Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#   Copyright (C) 2016-today Geminate Consultancy Services (<http://geminatecs.com>).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    "name": "Profit & Loss + Balance Sheet Analytic Groups",
    "version": "13.0.0.1",
    "author": "Geminate Consultancy Services",
    "website": "http://www.geminatecs.com",
    "category": "Account",
    "license": "Other proprietary", 
    "depends": ['account_reports'],
    "description": """
        Geminate comes with a feature of grouping based on analytic accounts on financial reports like balance sheet
        and profit & loss. it will tabularize all financial data from different charts of accounts under each analytic 
        account based on journal items. it will enable grouping only in case there is data available in that period / duration 
        or year.By that way, you can easily visualize the total amount utilized under that analytic account within the individual 
        chart of the account per duration.
    """,
    "summary": "Geminate comes with a feature of grouping based on analytic accounts on financial reports like balance sheet and profit & loss.",
    'data': [
            'views/search_view_templates.xml',
            ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
    'price': 69.99,
    'currency': 'EUR'
}
