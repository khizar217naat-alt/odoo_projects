{
    'name': 'Portal Reset Password',
    'version': '1.0',
    'summary': 'Custom password reset flow for portal users',
    'author': 'Tech Cog',
    'category': 'Website',
    'depends': ['base', 'website', 'auth_signup'],
    'data': [
        'views/reset_templates.xml',
        'views/override_login.xml',
    ],
    'installable': True,
    'application': False,
}
