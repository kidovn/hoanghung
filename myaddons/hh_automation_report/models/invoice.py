# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

import base64
from datetime import datetime,date
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class Invoice(models.Model):
    _inherit = 'intern.invoice'

    def send_pass_report_again(self):
        if self.env.user and (not self.env.user.signature or not self.env.user.email):
            raise ValidationError('Bạn cần thiết lập chữ ký và email để có thể gửi được email')
        ensure_one = False
        if not self.date_join_school:
            raise ValidationError(u"Chưa có thông tin ngày nhập học trúng tuyển")
        if not self.date_pass:
            raise ValidationError(u"Chưa có thông tin ngày trúng tuyển")
        if not self.date_departure:
            raise ValidationError(u"Chưa có thông tin ngày dự kiến xuất cảnh")

        if not self.dispatchcom1:
            raise ValidationError(u"Chưa có thông tin pháp nhân")

        if not self.job_vi or not self.job_jp:
            raise ValidationError(u"Chưa có thông tin ngành nghề")

        for intern in self.interns_clone:
            if intern.pass_exam and not intern.issues_raise:
                ensure_one = True

                break
        if ensure_one:
            for intern in self.interns_clone:
                if intern.pass_exam and not intern.issues_raise:
                    if not intern.enterprise:
                        raise ValidationError(u"Chưa có thông tin xí nghiệp của TTS %s" % intern.name)
                    elif not intern.place_to_work:
                        raise ValidationError(u"Chưa có thông tin địa điểm làm việc của TTS %s" % intern.name)

        report = self.env['hh.invoice.report'].search(
            [('custom_id', '=', 'THONG_BAO_TRUNG_TUYEN_%s' % self.room_pttt.name)])
        if report:
            self.send_mail_pass(report,True)
        return

    def confirm_pass(self):
        if self.env.user and (not self.env.user.signature or not self.env.user.email):
            raise ValidationError('Bạn cần thiết lập chữ ký và email để có thể gửi được email')
        super(Invoice,self).confirm_pass()
        report = self.env['hh.invoice.report'].search([('custom_id','=','THONG_BAO_TRUNG_TUYEN_%s'%self.room_pttt.name)])
        if report:
            self.send_mail_pass(report)

    def build_subject(self,report):
        if report.subject is not None:
            subject = report.subject.replace('%DON_HANG%','%s'%self.name).replace('%NGAY_THI%','%s'%datetime.strptime(self.date_exam_short,'%Y-%m-%d').strftime('%d/%m/%Y'))
            return subject
        return ''

    def build_body_content(self,report):
        if report.body_content is not None:
            body_content = report.body_content.replace('%DON_HANG%','%s' % self.name).replace(
                '%NGAY_THI%', '%s' % datetime.strptime(self.date_exam_short,'%Y-%m-%d').strftime('%d/%m/%Y'))
            if self.env.user and self.env.user.signature:
                body_content += "<div><br></div>--<br>%s" % self.env.user.signature
            return body_content
        return ''

    def send_mail_pass(self, report, again=False):
        mail_pool = self.env['mail.mail']

        # values = {'email_from':'doanhoangkien@gmail.com','reply_to':'doanhoangkien@gmail.com'}
        values = {}

        emails = report.emails.split(',')
        for i, email in enumerate(emails):
            if '<' in email and '>' in email:
                emails[i] = email[email.index('<') + 1:email.index('>')]

        subject = self.build_subject(report)
        if again:
            subject += u'(Chỉnh sửa)'

        values.update({'subject': subject})
        values.update({'email_to': ','.join(emails)})

        if report.emails_cc:
            emails_cc = report.emails_cc.split(',')
            for i, email in enumerate(emails_cc):
                if '<' in email and '>' in email:
                    emails_cc[i] = email[email.index('<') + 1:email.index('>')]

            values.update({'email_cc': ','.join(emails_cc)})

        values.update({'body_html': self.build_body_content(report)})

        msg_id = mail_pool.create(values)
        tmp_report = self.env['ir.actions.report.xml']._lookup_report(report.report_type.report_name)
        data, report_format = tmp_report.create(self._cr, self._uid, self.id, {}, context=self._context)
        # data, report_format = self.env['ir.actions.report.xml'].render_report(self.id,
        #                                                                       report.report_type.report_name,
        #                                                                       {})

        record = self.env['ir.attachment'].create({
            'name': report.name,
            'type': 'binary',
            'datas': base64.b64encode(data),
            'datas_fname': '%s.xlsx' % report.name,
            'res_model': 'invoice.invoice',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        msg_id.attachment_ids = [(6, 0, [record.id])]
        if msg_id:
            mail_pool.send([msg_id])

