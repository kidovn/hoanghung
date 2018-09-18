# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
import re
_logger = logging.getLogger(__name__)

class PageGroup(models.Model):
    _name = 'candidate.facebook'

    name = fields.Char('Tên page/group')
    address = fields.Char('Đường dẫn')
    friends = fields.One2many('hh.candidate','fbpage_id',string='Danh sách kết bạn')