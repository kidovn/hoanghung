# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.addons.hh_intern.models import intern_utils
import logging
_logger = logging.getLogger(__name__)

class InternPassReportAnnounce(models.AbstractModel):
    _name = 'report.hh_intern_pass_report.report_intern_pass_view'

    @api.multi
    def render_html(self, docids, data=None):
        _logger.info("DOcids %s"%docids)
        invoice = self.env['intern.invoice'].browse(docids[0])



        # self._cr.execute('SELECT intern_id FROM intern_order WHERE intern_order.invoice_id = %s' % docids[0])
        #
        # tmpresult = self._cr.dictfetchall()
        # if len(tmpresult) == 1:
        #     ids = tmpresult[0]['intern_id']
        #     if len(ids) == len(invoice.interns):
        #         interns = self.env['intern.intern'].browse(ids)
        #         invoice.interns = interns


        list_code = []
        list_code_prepare = []
        for intern in invoice.interns_clone:
            if intern.pass_exam:
                list_code.append(intern.id)
            if intern.preparatory_exam:
                list_code_prepare.append(intern.id)

        today = intern_utils.date_time_in_vn_lower(datetime.today().day,datetime.today().month,datetime.today().year)
        docargs = {
            'record': invoice,
            'codes':list_code,
            'codes_pre':list_code_prepare,
            'today':today
        }
        return self.env['report'].render('hh_intern_pass_report.report_intern_pass_view', values=docargs)