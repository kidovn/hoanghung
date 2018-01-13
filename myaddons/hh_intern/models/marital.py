# -*- coding: utf-8 -*-
from odoo import models, fields, api

import logging
import intern_utils

_logger = logging.getLogger(__name__)

class Marital(models.Model):
    _name = 'marital'
    _description = u'Tình trạng hôn nhân'
    _rec_name = 'name_in_vn'
    name_in_vn = fields.Char("Tiếng việt")
    name_in_jp = fields.Char("Tiếng Nhật")

    @api.multi
    def name_get(self):
        if not self.env.context.get('jp', False):
            return super(Marital, self).name_get()
        res = []
        for record in self:
            res.append((record.id, record.name_in_jp))
        return res