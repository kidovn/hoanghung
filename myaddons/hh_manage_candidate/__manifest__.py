# -*- coding: utf-8 -*-
{
    'name': "Candidate ",

    'summary': """
        Quản lý thông tin ứng viên""",

    'description': """
        Quản lý thông tin ứng viên
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
                'hh_intern','hh_schedule_notification','report_xlsx'
                ],


    # always loaded
    'data': [
        'security/base_security.xml',
        'views/task.xml',
        'views/candidate_view.xml',
        'views/candidate_menu.xml',
        'views/facebook_view.xml',
        'views/facebook_menu.xml',
        'views/styles.xml',
        'security/ir.model.access.csv',

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'qweb': [

    ],

    'application':  True,
}