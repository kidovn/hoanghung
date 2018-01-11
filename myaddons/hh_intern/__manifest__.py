# -*- coding: utf-8 -*-
{
    'name': "Intern ",

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
    'depends': ['base'],


    # always loaded
    'data': [
        'security/base_security.xml',
        'views/styles.xml',
        'views/intern_menu.xml',
        'views/intern_view.xml',
        'views/province_view.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],

    'application':  True,
}