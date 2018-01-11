# -*- coding: utf-8 -*-
from odoo import models, fields, api

import logging
import intern_utils

_logger = logging.getLogger(__name__)

class Certification(models.Model):
    _name = 'intern.certification'
    _description = u'Bằng cấp'
    _rec_name = 'name_in_vn'
    name_in_vn = fields.Char("Tên tiếng Việt")
    name_in_jp = fields.Char("Tên tiếng Nhật")

    @api.multi
    def name_get(self):
        if not self.env.context.get('jp', False):
            return super(Certification, self).name_get()
        res = []
        for record in self:
            _logger.info(record)
            res.append((record.id, record.name_in_jp))

        return res