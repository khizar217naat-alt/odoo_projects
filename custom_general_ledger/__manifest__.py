{
    'name': 'Custom General Ledger',
    'version': '1.0',
    'summary': 'Add Vendor and Customer fields to Sale Order and Invoice',
    'category': 'Sales',
    'author': 'Tech Cog',
    'depends': ['sale_management', 'account'],
    'data': [
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}