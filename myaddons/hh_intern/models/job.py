# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Job(models.Model):
    _name = 'intern.job'
    _description = u'Ngành nghề'
    name = fields.Char("Tiếng Việt")
    name_en = fields.Char("Tiếng Anh")
    name_jp = fields.Char("Tiếng Nhật")
    @api.multi
    def name_get(self):
        if not self.env.context.get('jp', False):
            return super(Job, self).name_get()
        res = []
        for record in self:
            res.append((record.id, record.name_jp))
        return res