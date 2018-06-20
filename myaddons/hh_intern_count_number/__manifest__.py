# -*- coding: utf-8 -*-
{
    'name': "Chinh sua listview",

    'summary': """
        Them cot dem cho listview""",

    'description': """
        Them cot dem cho listview
    """,

    'author': "KIDO",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['web'],

    'data': [
            'views/styles.xml',
             ],

    'qweb': [
        'static/src/xml/list_view_count.xml'
    ],
    'application':  True,
}