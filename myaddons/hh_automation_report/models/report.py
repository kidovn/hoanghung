# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

import os
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import xlwt
from odoo import report as odoo_report
import json
import ast
import base64
from io import BytesIO, StringIO

import re
from datetime import datetime,date
from odoo.addons.hh_intern.models import intern_utils
from odoo.addons.mail.models import mail_template

import sys
import logging
_logger = logging.getLogger(__name__)



class IrCron(models.Model):
    _name='hh.actionreport'

    _inherits = {'ir.cron': 'cron_job_id'}

    cron_job_id = fields.Many2one('ir.cron', string='Cron job', auto_join=True, ondelete="cascade", required=True)

    custom_id = fields.Char('Mã báo cáo', required=True)
    # name = fields.Char('Tên báo cáo', required=True)

    subject = fields.Char('Tiêu đề')
    body_content = fields.Text('Nội dung email')

    emails = fields.Char('Địa chỉ email nhận')
    emails_cc = fields.Char('Địa chỉ email cc')

    report_type = fields.Many2one('ir.actions.report.xml',string='Loại báo cáo',domain=[('model','=','hoanghung.report')])

    @api.model
    def create(self, vals):
        vals['function'] = 'excute_send_mail'
        vals['model'] = 'hh.actionreport'
        vals['args'] = False
        vals['doall'] = True
        vals['numbercall'] = -1
        res = super(IrCron, self).create(vals)
        res.args = res._ids
        return res

    @api.model
    def excute_send_mail(self, id):
        self = self.with_context(lang=u'vi_VN')
        cron = self.env['hh.actionreport'].browse(id)
        if cron:
            cron.method_direct_trigger()

    def method_direct_trigger(self):
        # _logger.info("TESTTT------ %d"%date.today().weekday())
        if date.today().weekday() == 6:
            return
        reload(sys)
        sys.setdefaultencoding("utf-8")

        data, report_format = self.env['ir.actions.report.xml'].render_report(self.report_type.id,
                                                                              self.report_type.report_name,
                                                                              {})
        subject = self.build_subject()

        record = None

        if data:
            record = self.env['ir.attachment'].create({
                'name': self.name,
                'type': 'binary',
                'datas': base64.b64encode(data),
                'datas_fname': '%s.xlsx' % subject,
                'res_model': 'account.invoice',
                'mimetype': 'application/vnd.ms-excel'
            })

        mail_pool = self.env['mail.mail']

        values = {}
        emails = self.emails.split(',')
        for i, email in enumerate(emails):
            if '<' in email and '>' in email:
                emails[i] = email[email.index('<') + 1:email.index('>')]
        values.update({'subject': subject})
        values.update({'email_to': ','.join(emails)})

        if self.emails_cc:
            emails_cc = self.emails_cc.split(',')
            for i, email in enumerate(emails_cc):
                if '<' in email and '>' in email:
                    emails_cc[i] = email[email.index('<') + 1:email.index('>')]

            values.update({'email_cc': ','.join(emails_cc)})

        values.update({'body_html': self.body_content})
        msg_id = mail_pool.create(values)
        if msg_id:
            if record:
                msg_id.attachment_ids = [(6, 0, [record.id])]
            mail_pool.send([msg_id])


    def build_subject(self,invoice=None):
        if self.subject is not None:
            subject = self.subject.replace('datetime.today()',datetime.today().strftime('%d/%m/%Y'))
            if invoice:
                subject = subject.replace('%DON_HANG%','%s'%invoice.name).replace('%THI_TUYEN%','%s'%invoice.date_exam_short)
            return subject
        return ''

    def build_body(self,invoice=None):
        if self.body_content is not None:
            body_content = self.body_content.replace('datetime.today()', datetime.today().strftime('%d/%m/%Y'))
            if invoice:
                body_content = body_content.replace('%DON_HANG%','%s' % invoice.name).replace('%THI_TUYEN%', '%s' % invoice.date_exam_short)
            return body_content
        return ''


class InvoiceReport(models.Model):
    _name = 'hh.invoice.report'
    custom_id = fields.Char('Mã báo cáo', required=True)
    name = fields.Char('Tên báo cáo', required=True)

    subject = fields.Char('Tiêu đề')
    body_content = fields.Text('Nội dung email')

    emails = fields.Char('Địa chỉ email nhận')
    emails_cc = fields.Char('Địa chỉ email cc')

    report_type = fields.Many2one('ir.actions.report.xml', string='Loại báo cáo',
                                  domain=[('model', '=', 'intern.invoice')])