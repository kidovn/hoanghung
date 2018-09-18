# -*- coding: utf-8 -*-
{
    'name': "Override base module in core",

    'summary': """
        Chỉnh sửa lại core odoo""",

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
    'depends': ['base','web'
                ],


    # always loaded
    'data': [
        # 'views/styles.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'qweb': [
        'static/src/xml/base.xml'
    ],

    'application':  True,
}