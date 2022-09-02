# -*- coding: utf-8 -*-

{
    'name'    : "Check-in & Checkout", 
    'summary' : """
    Driver's check-in and checkout
    """, 
    'author'  : "Quemari developers", 
    'category': "Inventory", 
    'website' : "http://www.quemari.com",
    'depends' : [
        'stock', 
        'website',
    ],
    'data'    : [
        'security/ir.model.access.csv',

        'views/check_in_checkout_views.xml',

        'views/portal_templates.xml',
    ],
}