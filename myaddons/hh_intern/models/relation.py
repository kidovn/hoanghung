# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Relation(models.Model):
    _name = 'relation'
    _description = u'Quan hệ với TTS'
    _rec_name = 'relation'
    relation = fields.Char("Tiếng Việt")
    relation_jp = fields.Char("Tiếng Nhật")

    @api.multi
    def name_get(self):
        if not self.env.context.get('jp', False):
            return super(Relation, self).name_get()
        res = []
        for record in self:
            res.append((record.id, record.relation_jp))
        return res