import odoo
import odoo.http as http
from odoo.http import request


class PopupController(odoo.http.Controller):

    @http.route('/popup_notifications/notify', type='json', auth="none")
    def notify(self):
        user_id = request.session.get('uid')
        return request.env['popup.notification'].sudo().search(
            [('partner_ids', '=', user_id)]
        ).get_notifications()

    @http.route('/popup_notifications/notify_ack', type='json', auth="none")
    def notify_ack(self, notif_id, type='json'):
        notif_obj = request.env['popup.notification'].sudo().browse([notif_id])
        user_id = request.session.get('uid')
        notif_obj.partner_ids = [(3, user_id)]
        if not notif_obj.partner_ids or len(notif_obj.partner_ids.ids) == 0:
            notif_obj.unlink()
