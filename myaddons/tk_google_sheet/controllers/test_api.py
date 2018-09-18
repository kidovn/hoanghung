# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request
from odoo.tools import config as odoo_config
import logging
from collections import OrderedDict

_logger = logging.getLogger(__name__)


class TkGoogleSheetApiController(http.Controller):
    @http.route('/api/googlesheet/test', methods = ['GET'], type = "http", auth = 'none', csrf = False)
    def googlesheet_test(self, **kw):
        db = kw['db'] if 'db' in kw else odoo_config.get('db_name', None)
        if not db:
            return json.dumps({
                'status': 'ERROR',
                'msg': 'Yeu cau chon db de thao tac bang cach truyen vao url ?db=...'
            })

        http.request.env['tk.google.sheet.dashboard'].logistic_returned_dashboard()

        return json.dumps({
            'status': 'OK',
            'msg': 'Nice day'
        })

    @http.route('/api/finance/get_mq_json_body', type="http", auth='none', csrf=False)
    def get_mq_json_body(self, **kw):
        db = kw['db'] if 'db' in kw else odoo_config.get('db_name', None)
        if not db:
            return json.dumps({
                'status': 'ERROR',
                'msg': 'Yeu cau chon db de thao tac bang cach truyen vao url ?db=...'
            })

        finance_mq_id = kw['id'] if 'id' in kw else None
        if not finance_mq_id:
            return json.dumps({
                'status': 'ERROR',
                'msg': 'Yeu cau truyen message id vao'
            })

        request.session.db = db
        mq = request.env['tk.logistic.message'].sudo().search([('id', '=', finance_mq_id)], limit=1)

        if mq:
            return mq.json_body
        else:
            return json.dumps({
                'status': 'ERROR',
                'msg': 'Khong tim thay mq trong he thong'
            })
