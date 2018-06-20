# -*- coding: utf-8 -*-
from odoo import models, fields, api
import intern_utils

class Job(models.Model):
    _name = 'intern.job'
    _description = u'Ngành nghề'
    name = fields.Char("Tiếng Việt")
    name_en = fields.Char("Tiếng Anh")
    name_jp = fields.Char("Tiếng Nhật")

    # @api.onchange('name')
    # def change_name(self):
    #     if self.name:
    #         self.name_without_signal = intern_utils.no_accent_vietnamese(self.name)

    @api.multi
    def name_get(self):
        if not self.env.context.get('jp', False):
            return super(Job, self).name_get()
        res = []
        for record in self:
            res.append((record.id, record.name_jp))
        return res

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     if name:
    #         args = args or []
    #         recs = self.search([('name_without_signal', 'ilike', intern_utils.no_accent_vietnamese(name))] + args, limit=limit)
    #         return recs.name_get()
    #     else:
    #         return super(Job, self).name_search(name, args, operator, limit)