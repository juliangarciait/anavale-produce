# See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner Credit Limit',
    'version': '13.0.1.0.0',
    'category': 'Partner',
    'license': 'AGPL-3',
    'author': 'Tiny, Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'maintainer': 'Serpent Consulting Services Pvt. Ltd.',
    'summary': 'Set credit limit warning',
    'depends': [
        'sale_management', 'anavale'
    ],
    'data': [
        'views/partner_view.xml',
        'security/groups.xml',
    ],
    'installable': True,
    'auto_install': False,
}
