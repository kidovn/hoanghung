# -*- coding: utf-8 -*-
{
    'name': "Lap lich notification ",

    'summary': """
        Lap lich notification""",

    'description': """
        Lap lich notification
    """,

    'author': "KIDO",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','base_action_rule', 'web_calendar'
                ],


    # always loaded
    'data': [
        'views/alarm_view.xml',
        'views/alarm_menu.xml',
        'views/alarm_template.xml',
        'data/alarm_data.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],

    'application':  True,
}