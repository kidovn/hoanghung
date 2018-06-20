# -*- coding: utf-8 -*-

from odoo import api, fields, models

from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ReportWizard(models.TransientModel):
    _name = "invoice.wizard"
    name = 'Tiến độ đơn hàng'
    room_pttt = fields.Many2one('department', string='Phòng PTTT',domain=[('room_type','=','1')])

    def generate_report(self):
        if self.room_pttt:
            return {
                'name': 'Report',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target': 'current',
                'url': 'vi_VN/report/pdf/hh_invoice_progress_report.report_invoice_progress_view/%d'%self.room_pttt.id
            }
            # context = self._context.copy()
            # context.update({'room_pttt':self.room_pttt.id})
            # return {
            #     'type': 'ir.actions.report.xml',
            #     'report_type':"qweb-html",
            #     'display_name':u'Phòng',
            #     'report_name': 'hh_invoice_progress_report.report_invoice_progress_view',
            #     'context':context,
            #     'datas':{'test':'test'}
            #
            # }
        else:
            raise ValidationError('Bạn chưa chọn phòng PTTT')
