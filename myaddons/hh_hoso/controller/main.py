# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request,Response
from odoo.addons.web.controllers.main import serialize_exception,content_disposition
from docx.enum.shape import WD_INLINE_SHAPE

from cStringIO import StringIO
from io import BytesIO
from docxtpl import DocxTemplate, InlineImage, CheckedBox, InlineShapeRec
from docx.shared import Mm, Inches, Pt
from docx import Document

import re
from tempfile import NamedTemporaryFile
import os
import json
import operator
from odoo.exceptions import AccessError, UserError
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlwt
from datetime import datetime, date
from docxtpl import DocxTemplate, InlineImage, CheckedBox, CheckBox, RichText, Tick

from odoo.addons.hh_intern.models import intern_utils
import zipfile

import sys
import io
# if os.name == 'nt':
#     import pythoncom
#     import win32com.client
import csv
import logging
_logger = logging.getLogger(__name__)


class Report(http.Controller):

    # @http.route('/web/dataset/search_data_for_report', type='json', auth="user")
    # def search_data_for_report(self, model, fields=False, domain=None,date_options=None):
    #
    #
    #     records = None
    #     # if model == 'intern.internclone':
    #     Model = request.env['intern.internclone']
    #     groups = Model.read_group(domain['intern']+domain['internclone'], fields.append('intern_id'),
    #                                  ['intern_id'])
    #     ids = []
    #     for group in groups:
    #         ids.append(group['intern_id'][0])
    #
    #     # Model_intern = request.env['intern.intern']
    #     records_tmp = Model.search_read([['intern_id','in',ids]],fields.append('intern_id'))
    #
    #     def _uniquify_list(seq):
    #         seen = {}
    #         invoice_ids = []
    #         for x in seq:
    #             if x['intern_id'][0] in seen:
    #                 if x['promoted']:
    #                     invoice_ids.append(x['invoice_id'][0])
    #
    #                     seen[x['intern_id'][0]]['invoices_promoted'] = seen[x['intern_id'][0]]['invoices_promoted'] + [x['invoice_id'][0]]
    #                     if x['confirm_exam'] and not x['escape_exam']:
    #                         seen[x['intern_id'][0]]['invoices_exam'] = seen[x['intern_id'][0]]['invoices_exam'] + [x['invoice_id'][0]]
    #                     if x['pass_exam']:
    #                         seen[x['intern_id'][0]]['invoices_pass'] = seen[x['intern_id'][0]]['invoices_pass'] + [x['invoice_id'][0]]
    #                     if x['preparatory_exam']:
    #                         seen[x['intern_id'][0]]['invoices_preparatory'] = seen[x['intern_id'][0]]['invoices_preparatory'] + [
    #                             x['invoice_id'][0]]
    #
    #                     seen[x['intern_id'][0]]['issues_before'] = seen[x['intern_id'][0]]['issues_before'] + x['issues_before']
    #                     seen[x['intern_id'][0]]['issues_after'] = seen[x['intern_id'][0]]['issues_after'] + x['issues_after']
    #                     seen[x['intern_id'][0]]['admission_late'] = seen[x['intern_id'][0]]['admission_late'] + x['admission_late']
    #
    #                     seen[x['intern_id'][0]]['visa_failure'] = seen[x['intern_id'][0]]['visa_failure'] or x['visa_failure']
    #                     seen[x['intern_id'][0]]['check_heath_before_departure'] = seen[x['intern_id'][0]]['check_heath_before_departure'] or x['check_heath_before_departure']
    #                     seen[x['intern_id'][0]]['check_before_fly'] = seen[x['intern_id'][0]]['check_before_fly'] or x['check_before_fly']
    #                     seen[x['intern_id'][0]]['departure'] = seen[x['intern_id'][0]]['departure'] or x['departure']
    #
    #             else:
    #                 if x['promoted']:
    #                     x['invoices_promoted'] = [x['invoice_id'][0]]
    #                     if x['confirm_exam'] and not x['escape_exam']:
    #                         x['invoices_exam'] = [x['invoice_id'][0]]
    #                     if x['pass_exam']:
    #                         x['invoices_pass'] = [x['invoice_id'][0]]
    #                     if x['preparatory_exam']:
    #                         x['invoices_preparatory'] = [x['invoice_id'][0]]
    #                 seen[x['intern_id'][0]] = x
    #
    #         return seen.values(),invoice_ids
    #
    #     records, invoices = _uniquify_list(records_tmp)
    #
    #
    #     if records is not None:
    #         return {'length':len(records),
    #                 'records':records}
    #     return {
    #         'length': 0,
    #         'records': []
    #     }

        # records = Model.search_read(domain, fields,
        #                             offset=offset or 0, limit=limit or False, order=sort or False)
        # if not records:
        #     return {
        #         'length': 0,
        #         'records': []
        #     }
        # if limit and len(records) == limit:
        #     length = Model.search_count(domain)
        # else:
        #     length = len(records) + (offset or 0)
        # return {
        #     'length': length,
        #     'records': records
        # }



    def from_data(self, fields, rows):
        if len(rows) > 65535:
            raise UserError(_('There are too many rows (%s rows, limit: 65535) to export as Excel 97-2003 (.xls) format. Consider splitting the export.') % len(rows))

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')

        for i, fieldname in enumerate(fields):
            worksheet.write(0, i, fieldname)
            worksheet.col(i).width = 8000 # around 220 pixels

        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD HH:mm:SS')

        for row_index, row in enumerate(rows):
            for cell_index, cell_value in enumerate(row):
                cell_style = base_style
                if isinstance(cell_value, basestring):
                    cell_value = re.sub("\r", " ", cell_value)
                elif isinstance(cell_value, datetime.datetime):
                    cell_style = datetime_style
                elif isinstance(cell_value, datetime.date):
                    cell_style = date_style
                worksheet.write(row_index + 1, cell_index, cell_value, cell_style)

        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return data



    @http.route('/web/dataset/make_report',type='http', auth="user")
    @serialize_exception
    def make_report(self, data, token):
        params = json.loads(data)

        model, fields, domain = \
            operator.itemgetter('model', 'fields', 'domain')(params)
        if 'sort' in params:
            sort =params['sort']
        else:
            sort = False
        Model = request.env[model]

        fields_name = [field['name'] for field in fields]
        fields_header = [field['string'] for field in fields]

        #
        # records = Model.search_read(domain, fields,
        #                             order=sort or False)

        records = Model.search(domain,offset = 0, limit = False,order=sort)

        raw_data = False
        import_data = records.export_data(fields_name, raw_data).get('datas', [])



        return request.make_response(self.from_data(fields_header,import_data),
                                     headers=[('Content-Disposition',
                                               content_disposition('test.xls')),
                                              ('Content-Type', 'application/vnd.ms-excel')],cookies={'fileToken': token})




    # @http.route('/web/binary/download_document_test', type='http', auth="public")
    # def download_cv(self, model, id, filename=None, **kwargs):
    #     invoice = request.env[model].browse(int(id))
    #     request._cr.execute('SELECT intern_id FROM intern_order WHERE intern_order.invoice_id = %s' % id)
    #     tmpresult = request._cr.dictfetchall()
    #     if len(tmpresult) == 1:
    #         ids = tmpresult[0]['intern_id']
    #         if len(ids) == len(invoice.interns):
    #             interns = request.env['intern.intern'].browse(ids)
    #             invoice.interns = interns
    #
    #     document = request.env['intern.document'].search([('name', '=', 'CV')], limit=1)
    #     finalDoc = invoice.createHeaderDoc()
    #     if os.name == 'nt':
    #         tempFile = NamedTemporaryFile(delete=False)
    #         _logger.info("DOC  %s ---  %s"%(finalDoc.name,tempFile.name))
    #         in_file = os.path.abspath(finalDoc.name)
    #         out_file = os.path.abspath(tempFile.name)
    #         pythoncom.CoInitialize()
    #         word = win32com.client.gencache.EnsureDispatch('Word.Application')
    #         doc = word.Documents.Open(in_file)
    #         # doc.SaveAs(out_file, FileFormat=17)
    #         # doc.Close()
    #         # word.Quit()
    #         # pythoncom.CoUninitialize()
    #         # with open(out_file.name, 'rb') as f:
    #         #     g = io.BytesIO(f.read())
    #         #
    #         #     return request.make_response(g,
    #         #                                     [('Content-Type', 'application/octet-stream'),
    #         #                                     ('Content-Disposition', content_disposition('test.pdf'))])
    #
    #
    #         # with open(finalDoc.name, 'rb') as f:
    #         #     g = io.BytesIO(f.read())
    #         #
    #         #     return request.make_response(g,
    #         #                                     [('Content-Type', 'application/octet-stream'),
    #         #                                     ('Content-Disposition', content_disposition('test.docx'))])
    #
    #     return Response("[error text]", status=400)

    @http.route('/web/binary/download_list_intern', type='http', auth="public")
    def download_list_intern(self, **kwargs):

        invoices = request.env['intern.invoice'].search([])

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        base_style = xlwt.easyxf('align: wrap yes')
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD')

        worksheet.write(0,0,u'Tên',base_style)
        worksheet.write(0,1,u'CMND/Thẻ CC',base_style)
        worksheet.write(0,2, u'Đơn hàng', base_style)
        worksheet.write(0,3,u'Ngày lập hồ sơ',base_style)
        worksheet.write(0,4,u'Ngày sinh',base_style)
        worksheet.write(0,5,u'Tuổi',base_style)

        counter = 1
        for invoice in invoices:
            for intern in invoice.interns_pass:
                if intern.cmnd_or_tcc !=None and invoice.date_create_letter_promotion_short !=None:
                    worksheet.write(counter, 0, u'%s'%intern.name, base_style)
                    worksheet.write(counter, 1, intern.cmnd_or_tcc, base_style)
                    worksheet.write(counter, 2, u'%s'%invoice.name, base_style)
                    worksheet.write(counter, 3, invoice.date_create_letter_promotion_short, date_style)
                    worksheet.write(counter, 4, intern.date_of_birth_short, date_style)
                    worksheet.write(counter, 5, u'%s'%str(intern_utils.get_age_jp(invoice.date_create_letter_promotion_short,intern.day, intern.month,intern.year)), base_style)
                    counter = counter+1

        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return request.make_response(data,
                                     headers=[('Content-Disposition',
                                               content_disposition('test.xls')),
                                              ('Content-Type', 'application/vnd.ms-excel')])