# -*- coding: utf-8 -*-
from odoo import models, fields, api

from tempfile import TemporaryFile, NamedTemporaryFile
from io import BytesIO
from datetime import datetime, date
from docxtpl import DocxTemplate, InlineImage, CheckedBox, CheckBox, RichText, Tick
from docx.shared import Mm, Inches
from docx import Document
import os
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class Candidate(models.Model):
    _inherit = 'hh.candidate'


    # @api.model
    # def create(self,vals):
    #     super(Candidate,self).create(vals)
    #     if '':
    #         values = {'status': 'draft', 'title': u'Thông báo',
    #                   'message': u'Bạn có cuộc gọi cho ' % self.name,
    #                   'partner_ids': [(6, 0, [self.id])]
    #                   }
    #         self.env['popup.notification'].create(values)
