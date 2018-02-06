# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class MyDocument(models.Model):
    _name = 'intern.document'
    _description = u'Các loại văn bản, báo cáo'
    name = fields.Char("Tên", required=True)
    note = fields.Text("Ghi chú")
    file_name = fields.Char("Tên file")
    attachment = fields.Binary('Văn bản mẫu', required=True)


