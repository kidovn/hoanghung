import babel.messages.pofile
import base64
import csv
import datetime
import functools
import glob
import hashlib
import imghdr
import itertools
import jinja2
import json
import logging
import operator
import os
import re
import sys
import time
import werkzeug.utils
import werkzeug.wrappers
import zlib
from xml.etree import ElementTree
from cStringIO import StringIO


import odoo
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_resource_path
from odoo.tools import topological_sort
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception
from odoo.exceptions import AccessError, UserError
from odoo.models import check_method_name
from odoo.addons.web.controllers.main import Export,ExportFormat, ExcelExport, Reports

_logger = logging.getLogger(__name__)

def serialize_exception(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            _logger.exception("An exception occured during an http request")
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return werkzeug.exceptions.InternalServerError(json.dumps(error))
    return wrap

class MyExport(Export):

    @http.route('/web/export/formats', type='json', auth="user")
    def formats(self):
        """ Returns all valid export formats

        :returns: for each export format, a pair of identifier and printable name
        :rtype: [(str, str)]
        """
        return [
            # {'tag': 'csv', 'label': 'CSV'},
            {'tag': 'xlsx', 'label': 'Excel', 'error': None if xlsxwriter else "XLWT required"},
        ]

class MyExportFormat(ExportFormat):
    def base(self, data, token):
        params = json.loads(data)
        model, fields, ids, domain, import_compat = \
            operator.itemgetter('model', 'fields', 'ids', 'domain', 'import_compat')(params)

        Model = request.env[model].with_context(**params.get('context', {}))
        records = Model.browse(ids) or Model.search(domain, offset=0, limit=False, order=False)

        if not Model._is_an_ordinary_table():
            fields = [field for field in fields if field['name'] != 'id']

        field_names = map(operator.itemgetter('name'), fields)
        import_data = records.export_data(field_names, self.raw_data).get('datas',[])

        if import_compat:
            columns_headers = field_names
        else:
            columns_headers = [val['label'].strip() for val in fields]


        return request.make_response(self.from_data(columns_headers, import_data),
            headers=[('Content-Disposition',
                            content_disposition(self.filename(model))),
                     ('Content-Type', self.content_type)],
            cookies={'fileToken': token})

class MyExcelExport(ExportFormat, http.Controller):
    # Excel needs raw data to correctly handle numbers and date values
    raw_data = True

    @http.route('/web/export/xlsx', type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        return self.base(data, token)

    @property
    def content_type(self):
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def filename(self, base):
        return base + '.xlsx'

    def from_data(self, fields, rows):
        if len(rows) > 65535:
            raise UserError(_('There are too many rows (%s rows, limit: 65535) to export as Excel 97-2003 (.xls) format. Consider splitting the export.') % len(rows))
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        worksheet = workbook.add_worksheet('Sheet 1')

        header_style = workbook.add_format(
            {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'fg_color': '#96b55e'})
        title_style = workbook.add_format({'bold': True})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        date_style = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1,'num_format':'DD-MM-YYYY'})
        datetime_style = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1,'num_format':'DD-MM-YYYY HH:mm:SS'})

        for i, fieldname in enumerate(fields):
            if i == 0:
                worksheet.write(0, i, 'STT', header_style)
                continue
            worksheet.write(0, i, fieldname,header_style)
            # worksheet.col(i).width = 8000 # around 220 pixels
            worksheet.set_column(i, i, 18)

        # base_style = xlwt.easyxf('align: wrap yes')
        # date_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD')
        # datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD HH:mm:SS')

        for row_index, row in enumerate(rows):
            for cell_index, cell_value in enumerate(row):
                if cell_index == 0:
                    worksheet.write(row_index + 1, cell_index, u'%d'%(row_index+1), center)
                    continue
                cell_style = center
                if isinstance(cell_value, basestring):
                    cell_value = re.sub("\r", " ", cell_value)
                    worksheet.write(row_index + 1, cell_index, cell_value, cell_style)
                elif isinstance(cell_value, datetime.datetime):
                    cell_style = datetime_style
                    worksheet.write_datetime(row_index + 1, cell_index, cell_value, cell_style)
                elif isinstance(cell_value, datetime.date):
                    cell_style = date_style
                    worksheet.write_datetime(row_index + 1, cell_index, cell_value, cell_style)


        workbook.close()
        fp.seek(0)
        data = fp.read()
        fp.close()
        return data

class MyReports(Reports):

    TYPES_MAPPING = {
        'doc': 'application/vnd.ms-word',
        'html': 'text/html',
        'odt': 'application/vnd.oasis.opendocument.text',
        'pdf': 'application/pdf',
        'sxw': 'application/vnd.sun.xml.writer',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }