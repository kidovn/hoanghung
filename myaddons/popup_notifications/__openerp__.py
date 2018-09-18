# -*- coding: utf-8 -*-
{
    'name': 'Popup notifications',
    'version': '1.1',
    'category': 'Extra Tools',
    'summary': 'Use popup notification to develop your modules',
    'description': '''
The app is a tool of generating popups similar to calendar events alarims in your own modules
* Popup is generated Odoo for users
* Popup is invoked each 3 minutes by standard Odoo javascript cron jobs
* You may close the popup just by clicling "Ok"
    ''',
    'auto_install': False,
    'author': 'IT Libertas',
    'website': 'https://odootools.com',
    'depends': [
        'base','hh_intern','hh_manage_candidate'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/popup_notifications.xml',
            ],
    'qweb': [
        'static/xml/base_popup.xml',
            ],
    'js': [

            ],
    'demo': [

            ],
    'test': [

            ],
    'license': 'AGPL-3',
    'images': ['static/description/main.png'],
    'update_xml': [],
    'application':True,
    'installable': True,
    'private_category':False,
    'external_dependencies': {
    },

}
