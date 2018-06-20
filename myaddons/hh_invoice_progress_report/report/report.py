# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.addons.hh_intern.models import intern_utils
import logging
_logger = logging.getLogger(__name__)

class InvoiceProgressReport(models.AbstractModel):
    _name = 'report.hh_invoice_progress_report.report_invoice_progress_view'

    @api.multi
    def render_html(self, docids, data=None):
        _logger.info("DOcids %s"%docids)
        department = self.env['department'].browse(docids)
        invoices = self.env['intern.invoice'].search([('status','=','2'),('room_pttt','=',docids)])

        # list_code = []
        # list_code_prepare = []
        # for intern in invoice.interns_clone:
        #     if intern.pass_exam:
        #         list_code.append(intern.id)
        #     if intern.preparatory_exam:
        #         list_code_prepare.append(intern.id)

        today = intern_utils.date_time_in_vn_lower(datetime.today().day,datetime.today().month,datetime.today().year)
        _logger.info("SIZE %d" % len(invoices))
        docargs = {
            'record': invoices,
            'department':department,
            'today':today
        }
        return self.env['report'].render('hh_invoice_progress_report.report_invoice_progress_view', values=docargs)