# -*- coding: utf-8 -*-
{
    'name': 'Stock Picking Cancel and Reset',
    "author": "Edge Technologies",
    'version': '13.0.1.8',
    'live_test_url': "https://youtu.be/ZTdzRLz0Leo",
    "images":['static/description/main_screenshot.png'],
    'summary': "App Cancel stock picking order cancel delivery order cancel receipt cancel picking cancel internal transfer cancel internal picking cancel reset stock picking reset delivery reverse stock picking reverse delivery cancel Rectify stock picking reset picking",
    'description': """ 
Using this app user can Cancel and Reset Done Delivery order and incoming shipment, Same works for all kind of picking
cancel stock picking cancel delivery order cancel incoming shipment cancel internal transfer cancel internal picking cancel
reset stock picking reset delivery order reset incoming shipment reset internal transfer reset internal picking reset
cancel and reset stock picking cancel and reset delivery order cancel and reset incoming shipment cancel and reset internal transfer cancel and reset internal picking reset
reverse stock picking reverse delivery order reverse incoming shipment reverse internal transfer reverse internal picking reverse cancel order cancel shipment reset shipment cancel
cacel vendor picking cancel customer delivery order reset shipment order cancel shipment order reset shipment order reset
Cancel Stock picking apps allow to cancel delivery order, shipment, internal transfer and picking quickly even if it's in done stage. If you have inventory valuation "Automated" as "Real-Time" then its also cancelled generated Stock journal entry. When you cancel stock picking(Delivery/Shipment) then product quantity get reset and generated stock move got cancelled.This apps can be use when user made mistake while process the delivery order and vendor shipment, sometimes user receive the wrong shipment or proceed wrong product quantity on warehouse,Same for delivery sometimes user can proceed the wrong delivery order or proceed with wrong quantity. When User Proceed and picking become done after that on Odoo there is no ractify option. Our apps helps to ractify any picking like delivery order, shipment or internal transfer on Odoo ERP at any stage and user can reset it to draft and have chance to correct it. Don't worry all the stock balance/quant and accounting entries will be effected properly
Ractify stock picking Ractify delivery order Ractify incoming shipment Ractify internal transfer Ractify internal picking cancel

    """,
    "license" : "OPL-1",
    'depends': ['base','sale_management','stock','account','purchase','stock_account'],
    'data': [
            'security/groups.xml',
            'views/picking_views.xml'
            ],
    'installable': True,
    'auto_install': False,
    'price': 30,
    'currency': "EUR",
    'category': 'Warehouse',

}

