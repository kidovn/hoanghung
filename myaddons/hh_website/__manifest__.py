# -*- coding: utf-8 -*-
{
    'name': "HH Website",

    'summary': """
        Show public data for all user""",

    'description': """
        Long description of module's purpose
    """,

    'author': "KIDO",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hh_intern','hh_hoso'
                ],


    # always loaded
    'data': [
        'views/website.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],

    # 'test': ['static/src/test/index.html','static/src/test/script.js','static/src/test/vnm.jpg'],

    'application':  True,
}