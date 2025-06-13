{
    'name': 'User Location Restriction',
    'version': '13.0.1.0.0',
    'summary': 'Restringe las ubicaciones visibles por usuario en stock y picking',
    'author': 'Tu Nombre',
    'category': 'Warehouse',
    'depends': ['base', 'stock'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/user_location_rules.xml',
        'views/res_users_view.xml',
        'views/stock_picking_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
} 