# -*- coding: utf-8 -*-
{
    'name': "Tk Accounting",

    'summary': "Teko Accounting",

    'description': """
Teko Accounting
====================
    """,

    'author': "Teko Finance Team",
    'website': "fm.teko.vn",

    'category': 'Teko Application',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        #'views/templates.xml',
        'views/kien_demo_view.xml',
        'views/menu.xml',
    ],
    # 'qweb': ['static/src/xml/*.xml'],
    # only loaded in demonstration mode
    'demo': [
       # 'demo/demo.xml',
    ],
    'qweb': [
        #'static/src/xml/*.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}