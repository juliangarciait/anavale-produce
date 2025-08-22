{
    'name': 'Quality Inspection',
    'version': '1.0',
    'summary': 'Quality inspection module for stock pickings',
    'description': 'Manage quality inspections linked to stock pickings.',
    'author': 'Tu Empresa',
    'depends': ['stock', 'purchase', 'repack_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/quality_inspect_views.xml',
        'views/quality_inspect_line_form.xml',
        'views/inspected_boxes_views.xml',
        'views/packaging_views.xml',
        'views/defect_views.xml',
        'views/stock_picking_view_inherit.xml',
    ],
    'installable': True,
    'application': False,
}
