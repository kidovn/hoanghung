# -*- coding: utf-8 -*-
{
    'name': "Tao bao cao",

    'summary': """
        Tạo bao cao""",

    'description': """
        Tạo maps
    """,

    'author': "KIDO",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hh_intern'],

    'data': [
            'views/report_view.xml',
            'views/templates.xml',
            'views/report_menu.xml',
            'data/schedule.xml',
            'security/ir.model.access.csv',
             ],

    'qweb': [
        'static/src/xml/report_template.xml'
    ],
    'application':  True,
}