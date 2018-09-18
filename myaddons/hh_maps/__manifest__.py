# -*- coding: utf-8 -*-
{
    'name': "intern maps",

    'summary': """
        Create/update/remove/Import interns""",

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
    'depends': ['base',
                'hh_intern','web_planner'
                ],


    # always loaded
    'data': [
        'views/province_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],

    # 'test': ['static/src/test/index.html','static/src/test/script.js','static/src/test/vnm.jpg'],

    'application':  True,
}