# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class Report(models.Model):
    _inherit = 'intern.invoice'

    @api.multi
    def download_pass_report(self):
        # ensure_one_pass = False
        # if self.status is not 2:
        #     raise ValidationError("Đơn hàng chưa chốt trúng tuyển")
        # for intern in self.interns_clone:
        #     if intern.pass_exam and not intern.cancel_pass:
        #         ensure_one_pass = True
        #         break
        # if not ensure_one_pass:
        #     raise ValidationError("Ko có TTS nào trúng tuyển")
        # return {
        #     'type': 'ir.actions.report.xml',
        #     'report_type':"qweb-html",
        #     'display_name':u'TB trúng tuyển',
        #     'report_name': 'hh_intern_pass_report.report_intern_pass_view',  # mention your report name here
        # }
        if not self.date_pass:
            raise ValidationError(u"Chưa có thông tin ngày trúng tuyển")
        if not self.room_pttt:
            raise ValidationError(u"Chưa có thông tin phòng PTTT")
        if not self.date_join_school:
            raise ValidationError(u"Chưa có thông tin ngày nhập học TT")
        if not self.date_departure:
            raise ValidationError(u"Chưa có thông tin ngày xuất cảnh dự kiến")
        for intern in self.interns_pass_doc:
            if not intern.place_to_work:
                raise ValidationError(u"Chưa có thông tin địa điểm làm việc của TTS %s" % intern.name)
            elif not intern.enterprise:
                raise ValidationError(u"Chưa có thông tin xí nghiệp của TTS %s"%intern.name)

        return self.env['report'].get_action(self, 'intern.invoice.pass.xlsx',
                                             data=None)


    @api.multi
    def download_exam_report(self):
        return self.env['report'].get_action(self, 'intern.invoice.exam.xlsx',
                                             data=None)

    @api.multi
    def download_promoted_report(self):
        return self.env['report'].get_action(self, 'intern.invoice.promoted.xlsx',
                                             data=None)

    def send_pass_report_again(self):
        return