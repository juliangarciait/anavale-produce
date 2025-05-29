{
    'name': "Control de Calidad",
    'version': '1.0',
    'summary': "Gestión de inspecciones de calidad",
    'description': "Permite realizar inspecciones de calidad en recepciones de mercancía.",
    'author': "Tu Nombre",  # Reemplaza con tu nombre
    'category': 'Quality',
    'depends': ['stock', 'purchase'],
    'data': [
        'security/ir.model.access.csv',  # Archivo para permisos de acceso
        'views/quality_inspection_views.xml',
        'views/stock_purchase_views.xml',  # Nuevo archivo
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}