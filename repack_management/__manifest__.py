{
    'name': 'Repack Management',
    'version': '13.0.1.0.0',
    'summary': 'Manage repack processes for products',
    'description': """
        Este módulo permite gestionar procesos de repack:
        - Crear líneas de repack manualmente o desde líneas de venta
        - Seguimiento del estado de cada línea de repack
        - Gestión de productos de salida por calidad
        - Proceso diario automático de líneas de repack
    """,
    'category': 'Inventory',
    'author': 'Anavale',
    'depends': [
        'base',
        'stock',
        'sale_management',
        'product',
        'anavale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/repack_views.xml',
        'views/product_views.xml',
        'wizard/create_daily_repack_views.xml',
        'data/ir_cron.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
} 