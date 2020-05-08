{
    'name': 'Sale report with lots',
    'version': '13.0.2',
    'category': 'Sales Management',
    'summary': 'Agrega la opcion de seleccionar lote reporte de ventas',
    'description': """ Automatically lot number in inventory form Sale Order
    """,
    'price': 10,
    'currency': 'EUR',
    "author" : "Julian Garcia",
    'sequence': 1,
    "email": 'apps@maisolutionsllc.com',
    "website":'http://maisolutionsllc.com/',
    'license': 'OPL-1',
    'depends': ['account','sale_stock'],
    'data': [
            # 'views/bill_view.xml',
            #'view/sale_report_views.xml',

            # 'views/lot_view.xml'
             ],
    'qweb': [
        ],
    'images': ['static/description/main_screenshot.png'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
