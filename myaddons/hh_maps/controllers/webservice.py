# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
from odoo.addons.web.controllers.main import serialize_exception,content_disposition
import logging
from io import BytesIO
_logger = logging.getLogger(__name__)


class WebFormController(http.Controller):

    @http.route('/odoo/maps', type='http',
                auth='public', methods=['GET'])
    def index(self, **args):
        _logger.info('CONNECTION SUCCESSFUL')
        _logger.info(args)
        # request.uid = 1
        invoice_id = args.get('invoice',False)
        _logger.info("INVOICE  %s"%str(invoice_id))
        invoice = request.env['intern.invoice'].sudo().browse(int(invoice_id))
        request._cr.execute('SELECT intern_id FROM intern_order WHERE intern_order.invoice_id = %s' % invoice_id)
        tmpresult = request._cr.dictfetchall()
        if len(tmpresult) == 1:
            ids = tmpresult[0]['intern_id']
            if len(ids) == len(invoice.interns):
                interns = request.env['intern.intern'].sudo().browse(ids)
                invoice.interns = interns
        maps = {}

        # _logger.info("avatar %s "%request.httprequest.host_url)
        if invoice:
            for i,intern in enumerate(invoice.interns):
                mapschild = {}
                avatars = {}
                tts = ""
                if intern.province.id_map in maps:
                    mapschild = maps.get(intern.province.id_map)
                    tts = mapschild.get('tts')
                    tts = tts + ",%d"%(i+1)
                    avatars = mapschild.get('avatars')
                    avatars['%d' % (i + 1)] = "%sodoo/get_avatar?intern=%d" % (
                                            str(request.httprequest.host_url), intern.id)
                    mapschild['tts'] = tts
                    mapschild['avatars'] = avatars

                else:
                    mapschild['tieng_viet'] = intern.province.name
                    mapschild['tieng_nhat'] = intern.province.name_in_jp
                    tts = "%d"%(i+1)
                    mapschild['tts'] = tts
                    avatars['%d' % (i + 1)] = "%sodoo/get_avatar?intern=%d" % (
                        str(request.httprequest.host_url), intern.id)
                    mapschild['avatars'] = avatars
                    mapschild['className']= 'green'
                    mapschild['pos'] = {'x':intern.province.x_point,'y':intern.province.y_point}
                    mapschild['col'] = intern.province.column
                    mapschild['sort'] = intern.province.sort
                maps[intern.province.id_map] = mapschild

        listPro = []
        for key, value in maps.iteritems():
            listPro.append(value)
        def getKey(item):
            return item['sort']
        listPro.sort(key=getKey)

        maps_return = {}
        maps_return['title'] = invoice.name_of_guild
        maps_return['data'] = listPro

        return json.dumps(maps_return, ensure_ascii=False, encoding='utf8')

    @http.route('/odoo/get_avatar', type='http',
                auth='public', methods=['GET'])
    def get_avatar(self, **kwargs):
        intern_id = kwargs.get('intern', False)
        intern = request.env['intern.intern'].sudo().browse(int(intern_id))
        streamAvatar = BytesIO()
        if intern.avatar is not None:
            streamAvatar = BytesIO(intern.avatar.decode("base64"))

        return request.make_response(streamAvatar,
                                         [('Content-Type', 'image/jpeg'),
                                          ('Content-Disposition', content_disposition('avatar.jpeg'))])

