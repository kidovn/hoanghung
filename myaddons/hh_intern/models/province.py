# -*- coding: utf-8 -*-
from odoo import models, fields, api
import intern_utils

class Province(models.Model):
    _name= 'province'
    _description = u'Tỉnh/thành phố'
    name = fields.Char("Tên có dấu")
    distance_to_hn = fields.Integer("Khoảng cách tới Hà Nội")

    def getDistanceString(self):
        return u"ハノイ中心から約%d時間" % self.distance_to_hn

    def getNameWithoutSign(self):
        return intern_utils.no_accent_vietnamese(self.name)