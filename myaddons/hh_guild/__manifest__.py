# -*- coding: utf-8 -*-
{
    'name': "Nghiep doan ",

    'summary': """
        Danh sach nghiep doan""",

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
    'depends': [
                'hh_intern',
                ],


    # always loaded
    'data': [
        'views/guild_menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'qweb': [


    ],

    'application':  True,
}