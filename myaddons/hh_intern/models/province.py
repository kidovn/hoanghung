# -*- coding: utf-8 -*-
from odoo import models, fields, api
import intern_utils
import logging
_logger = logging.getLogger(__name__)

class Province(models.Model):
    _name= 'province'
    _description = u'Tỉnh/thành phố'
    name = fields.Char("Tên có dấu")
    distance_to_hn = fields.Integer("Khoảng cách tới Hà Nội")

    def getDistanceString(self):
        if self.name == u'Hà Nội':
            return u'ハノイ中心から約30分'
        return u"ハノイ中心から約%d時間" % self.distance_to_hn

    def getNameWithoutSign(self):
        return intern_utils.no_accent_vietnamese(self.name)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            args = args or []
            recs = self.search([('name', 'ilike', name)] + args, limit=limit)
            return recs.name_get()
        else:
            return super(Province, self).name_search(name, args, operator, limit)

class JapanProvince(models.Model):
    _name = 'japan.province'
    name = fields.Char('Tên tỉnh')