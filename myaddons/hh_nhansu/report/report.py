# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.addons.hh_intern.models import intern_utils
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import logging
_logger = logging.getLogger(__name__)


class ListBirthdayInMonth(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, invoices):
        report_name = u'Danh sách sinh nhật trong tháng %s'%data['month']
        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])
        title_style = workbook.add_format({'bold': True})
        bold = workbook.add_format({'bold': True,'align': 'center','valign': 'vcenter','border':1})
        center = workbook.add_format({'align': 'center','valign':   'vcenter','border':1})
        wrap = workbook.add_format({'text_wrap': True,'align': 'center','valign': 'vcenter','border':1})
        header_style = workbook.add_format({'bold': True,'text_wrap': True,'align': 'center','valign': 'vcenter','border':1,'fg_color': '#96b55e'})

        bold_no_border = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        wrap_no_border = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})

        row_id = 0
        #TITLE
        sheet.write(row_id, 0, report_name, title_style)
        row_id+=1

        #HEADER
        sheet.write(row_id,0,'STT',header_style)
        sheet.write(row_id,1,u'Họ tên',header_style)
        sheet.write(row_id,2,u'Ngày sinh',header_style)
        sheet.write(row_id,3,u'Giới tính',header_style)
        sheet.write(row_id,4,u'Phòng',header_style)
        row_id += 1

        employees = self.env['hh.employee'].search([('room_type','!=','7'),('active','=',True),('birth_month','=',int(data['month']))])
        for i,employee in enumerate(employees):
            sheet.write(row_id,0,'%d'%(i+1),center)
            sheet.write(row_id,1,u'%s'%employee.name,center)
            sheet.write(row_id,2,u'%s' % datetime.strftime(datetime.strptime(employee.date_of_birth, '%Y-%m-%d'),
                                                              '%d-%m-%Y'),center)
            if employee.gender == 'nu':
                sheet.write(row_id,3,u'Nữ',center)
            else:
                sheet.write(row_id,3,u'Nam',center)
            if employee.department_id:
                sheet.write(row_id,4,employee.department_id.name,center)
            else:
                sheet.write(row_id, 4,'',center)
            row_id+=1

        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 18)
        sheet.set_column(2, 2, 18)
        sheet.set_column(4, 4, 18)


ListBirthdayInMonth('report.employee.birthday.xlsx',
            'hoanghung.report')




