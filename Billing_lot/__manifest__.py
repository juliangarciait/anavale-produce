{
    'name': 'Billing Lot',
    'version': '13.0.2',
    'category': 'Sales Management',
    'summary': 'Agrega la opcion de seleccionar lote en el billing para seguimiento en el lote',
    'description': """ Automatically lot number in inventory form Sale Order
    """,
    'price': 10,
    'currency': 'EUR',
    "author" : "Julian Garcia",
    'sequence': 1,
    "email": 'apps@maisolutionsllc.com',
    "website":'http://maisolutionsllc.com/',
    'license': 'OPL-1',
    'depends': ['account.move'],
    'data': [
            'views/bill_view.xml',
             ],
    'qweb': [
        ],
    'images': ['static/description/main_screenshot.png'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
