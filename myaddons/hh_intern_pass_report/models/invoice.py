# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class Report(models.Model):
    _inherit = 'intern.invoice'

    @api.multi
    def download_pass_report(self):
        ensure_one_pass = False
        if self.status is not 2:
            raise ValidationError("Đơn hàng chưa chốt trúng tuyển")
        for intern in self.interns_clone:
            if intern.pass_exam and not intern.cancel_pass:
                ensure_one_pass = True
                break
        if not ensure_one_pass:
            raise ValidationError("Ko có TTS nào trúng tuyển")
        return {
            'type': 'ir.actions.report.xml',
            'report_type':"qweb-html",
            'display_name':u'TB trúng tuyển',
            'report_name': 'hh_intern_pass_report.report_intern_pass_view',  # mention your report name here
        }


