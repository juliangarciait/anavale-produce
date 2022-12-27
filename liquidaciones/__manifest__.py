# -*- encoding: utf-8 -*-
{
    'name': 'Liquidaciones ANAVALE',
    'version': '1.0',
    'category': 'Liquidaciones',
    'description': """
    Boton en cotizaciones, que muestra liquidaciones 
""",
    'author': 'ANAVALE, S. de R.L. de C.V.',
    'website': '',
    'depends': ['sale_management', 'odoo_report_xlsx'],
     # always loaded
    'data': [
         'views/settlement_views.xml',
         'views/button_settlements_views.xml',
         'security/ir.model.access.csv',
         'wizard/selection_views.xml',
         'reports/settlements_report_templates.xml',
         'reports/settlements_report_view.xml', 
         'reports/xlsx_report_template.xml'
    ],
    #Se agrega relación de assets
    #'assets': {
     #   'web.assets_backend': [
      #   'static/src/js/kanban_widget.js'
       # ],
   # },
    'installable': True,
    'auto_install': False,
}