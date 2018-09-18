# -*- coding: utf-8 -*-
{
    'name': "Kế toán",

    'summary': """
        Kế toán quản lý cọc""",

    'description': """
        Kế toán quản lý cọc
    """,

    'author': "KIDO",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hh_intern','auditlog'],

    'data': [
            'security/base_security.xml',
            'views/wizard.xml',
            'views/audit_view.xml',
            'views/intern_view.xml',
            'views/intern_menu.xml',
            'views/style.xml',
            'security/ir.model.access.csv',
             ],

    'qweb': [
        'static/src/xml/widget_template.xml'
    ],
    'application':  True,
}