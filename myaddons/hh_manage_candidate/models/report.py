# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.addons.hh_intern.models import intern_utils
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class RecuitmentTaskReport(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, reports):
        report_name = u'Báo cáo tuần từ %s-%s' % (data['start_date'], data['end_date'])
        sheet = workbook.add_worksheet(report_name[:31])

        # employees = fields.


# RecuitmentTaskReport('report.recuitment.task.xlsx',
#             'hoanghung.report')
