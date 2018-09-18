# -*- coding: utf-8 -*-
{
    'name': "Nhân sự ",

    'summary': """
        Nhân sự HH""",

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
                'hh_intern',
                # 'report','report_xlsx'
                ],


    # always loaded
    'data': [
        'security/base_security.xml',
        'views/wizard.xml',
        'views/employee.xml',
        'views/employee_menu.xml',
        'views/styles.xml',
        'security/ir.model.access.csv',
        # 'views/report_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'qweb': [

    ],

    'application':  True,
}