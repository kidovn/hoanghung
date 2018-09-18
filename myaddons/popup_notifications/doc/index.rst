PopUp Notifications
===================
* For each popup Odoo would generate a special instance of 'popup.notification'
* The field partner_ids - is a many2many relation to res.users object
* Each popup notification has a status. Possible values: 'draft', 'shown'. By default: 'draft'
* As soon as you pressed 'Ok', the status is changed to 'shown'. The notification would not be shown again


Example of use:
=====================

.. code:: python

    values = {
        'status': 'draft',
        'title': u'Be notified about',
        'message': '''Do not forget to
        send notification in  21.04.17''',
        'partner_ids': [(6, 0, [1, 2, 3])] # the list of users ids to notify
    }
    self.env['popup.notification'].create(values)