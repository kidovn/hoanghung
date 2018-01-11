# -*- coding: utf-8 -*-
from odoo import models, fields, api
import intern_utils
import logging
_logger = logging.getLogger(__name__)

class Translator(models.Model):
    _name = "intern.translator"
    _description = u'Phiên âm tiếng Nhật'
    _rec_name = 'vi_word'
    _sql_constraints = [
        ('vi_word_uniq', 'unique(vi_word)', "Từ này đã tồn tại"),
    ]

    vi_word = fields.Char("Tiếng Việt")
    jp_word = fields.Char("Tiếng Nhật")

    @api.onchange('vi_word')
    def test_change(self):
        if self.vi_word:
            self.vi_word = intern_utils.fix_accent_2(intern_utils.no_accent_vietnamese2(self.vi_word).upper())



    @api.model
    def create(self, vals):
        # vals['vi_word'] = intern_utils.fix_accent_2(intern_utils.no_accent_vietnamese2(vals['vi_word']).upper())
        _logger.info("word " + vals['vi_word'])
        return super(Translator, self).create(vals)

