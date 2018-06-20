# -*- coding: utf-8 -*-
from odoo import models, fields, api

import logging
import intern_utils

_logger = logging.getLogger(__name__)

class School(models.Model):
    _name = 'school'
    _description = u'Trường'
    _rec_name = 'name_in_vn'
    name_in_vn = fields.Char("Tên tiếng việt")
    name_in_jp = fields.Char("Tên tiếng Nhật")

    @api.multi
    def name_get(self):
        # if not self.env.context.get('jp', False):
        #     return super(School, self).name_get()
        res = []
        for record in self:
            # _logger.info(record)
            res.append((record.id, record.name_in_vn))

        return res