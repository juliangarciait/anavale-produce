{
    'name': 'Anavale Produce',
    'category': 'Uncategorized',
    'version': '0.1',
    'summary': 'Anavale Produce',
    'description': """ This module allows Purchase Order to select Lot from available Lots, 
    including in-transit lots.
    Warehouse has to be configured as a 'Receive goods in input and then stock (2 steps)'.
    """,
    "author" : "Mayte Montano",
    'sequence': 1,
    "email": 'mayte@eadminpro.com',
    "website":'http://eadminpro.com/',
    'depends': ['sale_stock'],
    'data': [
            'views/sale_view.xml',
            'views/stock_view.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
