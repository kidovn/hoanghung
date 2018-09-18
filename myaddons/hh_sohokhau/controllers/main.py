# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception,content_disposition
from docx.enum.shape import WD_INLINE_SHAPE

from io import BytesIO, StringIO
from docxtpl import DocxTemplate, InlineImage, CheckedBox
from docx.shared import Mm, Inches, Pt
# from docx import Document
from tempfile import NamedTemporaryFile
import os

from odoo.addons.hh_intern.models import intern_utils
import zipfile

import logging
_logger = logging.getLogger(__name__)

class CreateDocument(http.Controller):

    @http.route('/web/binary/download_shk', type='http', auth="public")
    def download_shk(self, id, filename=None, **kwargs):
        shk = request.env['intern.hokhau'].browse(int(id))

        return request.make_response(shk.generate_shk(),
                                     headers=[('Content-Disposition',
                                               content_disposition('hokhau.docx')),
                                              ('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')])


