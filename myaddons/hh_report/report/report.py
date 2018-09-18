# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.addons.hh_intern.models import intern_utils
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class ChiTieuTuyenDungXlsx(ReportXlsx):

    def count_target_working(self,date_string,month_report,year_report):
        date_start = datetime.strptime(date_string,'%Y-%m-%d')
        month = date_start.month + date_start.year*12
        month_diff = int(month_report) + int(year_report)*12 - month
        if date_start.day >= 15:
            month_diff -= 1
        if month_diff >= 9:
            return 9
        return month_diff

    # def count_target(self,employee,month_report,year_report):


    def generate_xlsx_report(self, workbook, data, invoices):
        # for obj in invoices:
            report_name = 'Bang Chi Tieu Tuyen Dung'
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            title_style = workbook.add_format({'bold': True})
            bold = workbook.add_format({'bold': True,'align': 'center','valign': 'vcenter','border':1})
            center = workbook.add_format({'align': 'center','valign':   'vcenter','border':1})
            wrap = workbook.add_format({'text_wrap': True,'align': 'center','valign': 'vcenter','border':1})
            header_style = workbook.add_format({'bold': True,'text_wrap': True,'align': 'center','valign': 'vcenter','border':1,'fg_color': '#96b55e'})

            bold_no_border = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
            wrap_no_border = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
            style_percent = workbook.add_format({'align': 'center','valign':   'vcenter','border':1, 'num_format': '0.00%'})


            row_id = 0
            #TITLE
            sheet.write(row_id, 0, u'TỔNG CHỈ TIÊU THEO PHÒNG TD HOÀNG HƯNG', title_style)

            row_id+=2

            date_start_month = datetime.strptime('%s-%s-01'% (data['year'], data['month']),'%Y-%m-%d') + relativedelta(months=1)

            invoices = self.env['intern.invoice'].search(
                [('status','>=',1),('date_exam_short', '>=', '%s-%s-01' % (data['year'], data['month'])),
                 ('date_exam_short', '<', date_start_month)])

            interns_ct = {}
            for invoice in invoices:
                for intern in invoice.interns_clone:
                    if intern.confirm_exam:
                        if interns_ct.has_key(intern.recruitment_employee.id):
                            interns_ct.update({intern.recruitment_employee.id: (interns_ct.get(intern.recruitment_employee.id)+1)})
                        else:
                            interns_ct.update({intern.recruitment_employee.id: 1})


            #TABLE HEADER
            room_tds = self.env['department'].search([('room_type','=','0')])




            for room_td in room_tds:
                sheet.write(row_id, 0, u'Phòng %s'%room_td.name, title_style)
                row_id +=1
                sheet.write(row_id, 0, u'STT', header_style)
                sheet.write(row_id, 1, u'Họ và tên cán bộ', header_style)
                sheet.write(row_id, 2, u'Chỉ tiêu khoán', header_style)
                sheet.write(row_id, 3, u'Chỉ tiêu thực hiện', header_style)
                sheet.write(row_id, 4, u'Tỉ lệ đạt(%)', header_style)

                row_id += 1
                counter = 1
                if room_td.manager:
                    sheet.write(row_id, 0, u'%d'%counter, bold)
                    sheet.write(row_id, 1, u'%s'%room_td.manager.name, bold)
                    sheet.write(row_id, 2, u'', bold)
                    sheet.write(row_id, 3, u'', bold)
                    sheet.write(row_id, 4, u'', bold)
                    counter += 1
                    row_id += 1

                employees = self.env['hh.employee'].search([('active','=',True),('department_id','=',room_td.id),('date_temp_work','<',datetime.strptime('15-%s-%s'%(data['month'],data['year']),'%d-%m-%Y'))])
                for employee in employees:
                    if not room_td.manager or employee.id != room_td.manager.id:
                        count_target = self.count_target_working(employee.date_temp_work, data['month'], data['year'])
                        if count_target>0:
                            sheet.write(row_id, 0, u'%d'%(counter), center)
                            sheet.write(row_id, 1, u'%s' % employee.name, center)

                            sheet.write(row_id, 2, count_target,center)
                            if interns_ct.has_key(employee.id):
                                sheet.write(row_id, 3, interns_ct.get(employee.id),center)
                            else:
                                sheet.write(row_id, 3, 0,center)
                            sheet.write_formula('E%d'%(row_id+1),'=D%d/C%d'%(row_id+1,row_id+1),style_percent)

                            counter += 1
                            row_id += 1

                sheet.write(row_id, 1, u'Cộng', center)
                sheet.write_formula('C%d'%(row_id+1),'=SUM(C%d:C%d)'%(row_id-counter-3,row_id),center)
                sheet.write_formula('D%d'%(row_id+1),'=SUM(D%d:D%d)'%(row_id-counter-3,row_id),center)
                sheet.write_formula('E%d' % (row_id + 1), '=D%d/C%d' % (row_id + 1, row_id + 1), style_percent)
                row_id += 1

            #
            sheet.set_column(0, 0, 10)
            sheet.set_column(1, 1, 20)
            sheet.set_column(2, 2, 10)
            sheet.set_column(3, 3, 10)
            sheet.set_column(4, 4, 10)
            # sheet.set_column(5, 5, 10)
            # sheet.set_column(6, 6, 10)
            # sheet.set_column(7, 7, 20)
            # sheet.set_column(8, 8, 7)
            # sheet.set_column(9, 9, 12)
            # sheet.set_column(10, 10, 12)
            # sheet.set_column(11, 11, 12)
            # sheet.set_column(12, 12, 12)


ChiTieuTuyenDungXlsx('report.hunt.target.xlsx',
            'hoanghung.report')


class ThongKeSoLieuNguonXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, reports):
        report_name = u'Thống kê số liệu nguồn T%s.%s'%(data['month'],data['year'] )
        # One sheet by partner
        sheet = workbook.add_worksheet(report_name[:31])
        title_style = workbook.add_format({'bold': True})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        header_style = workbook.add_format(
            {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'fg_color': '#96b55e'})

        bold_no_border = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        wrap_no_border = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})

        row_id = 0
        sheet.write(row_id, 1, report_name, title_style)
        row_id+=2

        sheet.write(row_id,0,'',header_style)
        sheet.write(row_id,1,'',header_style)
        sheet.write(row_id,2,u'BCĐ',header_style)
        sheet.write(row_id,3,u'DH',header_style)
        sheet.write(row_id,4,u'NH',header_style)
        sheet.write(row_id,5,u'Rút bỏ ĐH',header_style)
        sheet.write(row_id,6,u'Rút bỏ trúng tuyển',header_style)

        row_id+=1
        for i in range(1,13):
            sheet.write(row_id, 0, i, center)
            sheet.write(row_id, 1, u'Tháng %d'%i, center)
            if i == int(data['month']):
                date_start = datetime.strptime('%s-%s-01'%(data['year'],data['month']),'%Y-%m-%d')
                sources_nh = self.env['intern.source.history'].search_count([('date_enter_source','>=',date_start),('date_enter_source', '<', date_start+relativedelta(months=1)),('enter_source','=','1')])
                sources_dh = self.env['intern.source.history'].search_count([('date_enter_source','>=',date_start),('date_enter_source', '<', date_start+relativedelta(months=1)),('enter_source','=','2')])
                sources_bcd = self.env['intern.source.history'].search_count([('date_enter_source','>=',date_start),('date_enter_source', '<', date_start+relativedelta(months=1)),('enter_source','=','3')])
                sheet.write(row_id, 2, sources_nh, center)
                sheet.write(row_id, 3, sources_dh, center)
                sheet.write(row_id, 4, sources_bcd, center)
                # escape =
                issues = self.env['intern.internclone'].search_count([('date_escape_exam','>=',date_start),('date_escape_exam', '<', date_start+relativedelta(months=1)),('issues_raise','=',True)])
                cancel_passes = self.env['intern.internclone'].search_count([('date_cancel_pass','>=',date_start),('date_cancel_pass', '<', date_start+relativedelta(months=1)),('cancel_pass','=',True)])
                sheet.write(row_id, 5, issues, center)
                sheet.write(row_id, 6, cancel_passes, center)
            else:
                sheet.write(row_id, 2, u'', center)
                sheet.write(row_id, 3, u'', center)
                sheet.write(row_id, 4, u'', center)
                sheet.write(row_id, 5, u'', center)
                sheet.write(row_id, 6, u'', center)
            row_id += 1
        sheet.merge_range('A%d:B%d'%(row_id,row_id),u'Tổng',center)
        sheet.write_formula('C%d'%(row_id),'=SUM(C%d:C%d)'%(row_id-11,row_id-1),center)
        sheet.write_formula('D%d'%(row_id),'=SUM(D%d:D%d)'%(row_id-11,row_id-1),center)
        sheet.write_formula('E%d'%(row_id),'=SUM(E%d:E%d)'%(row_id-11,row_id-1),center)
        sheet.write_formula('F%d'%(row_id),'=SUM(F%d:F%d)'%(row_id-11,row_id-1),center)
        sheet.write_formula('G%d'%(row_id),'=SUM(G%d:G%d)'%(row_id-11,row_id-1),center)




ThongKeSoLieuNguonXlsx('report.intern.resources.xlsx',
                     'hoanghung.report')


class PhatSinhXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, reports):
        sheet = workbook.add_worksheet(u'Phat Sinh')
        invoices = self.env['intern.invoice'].search(
            [('date_exam_short', '>=', data['start_date']), ('date_exam_short', '<=', data['end_date'])])

        title_style = workbook.add_format({'bold': True})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        header_style = workbook.add_format(
            {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'fg_color': '#96b55e'})

        bold_no_border = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        wrap_no_border = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})

        row_id = 0
        sheet.write(row_id, 1, u'Danh sách rút bỏ trúng tuyển', title_style)

        row_id+=2

        interns_escape_exam = []
        interns_escape_pass = []
        for invoice in invoices:
            for intern in invoice.interns_clone:
                if intern.issues_raise:
                    interns_escape_exam.append(intern)
                elif intern.cancel_pass:
                    interns_escape_pass.append(intern)

        sheet.write(row_id, 0, u'STT', header_style)
        sheet.write(row_id, 1, u'Họ và tên', header_style)
        sheet.write(row_id, 2, u'Mã số', header_style)
        sheet.write(row_id, 3, u'Ngày nhập', header_style)
        sheet.write(row_id, 4, u'Năm sinh', header_style)
        sheet.write(row_id, 5, u'Quê quán', header_style)
        sheet.write(row_id, 6, u'Cán bộ tuyển dụng', header_style)
        sheet.write(row_id, 7, u'NĐ-Xí nghiệp', header_style)
        sheet.write(row_id, 8, u'TC lần 1', header_style)
        sheet.write(row_id, 9, u'TC lần 2', header_style)
        sheet.write(row_id, 10, u'TC lần 3', header_style)
        sheet.write(row_id, 11, u'Lý do rút bỏ', header_style)
        row_id += 1

        counter = 1
        for internclone in interns_escape_pass:
            # intern = self.env['intern.intern'].browse(internclone.intern_id)
            sheet.write(row_id, 0,counter,center)
            sheet.write(row_id, 1,internclone.intern_id.name,center)
            sheet.write(row_id, 2,internclone.intern_id.custom_id,center)
            if internclone.intern_id.date_enter_source:
                sheet.write(row_id, 3,datetime.strptime(internclone.intern_id.date_enter_source, '%Y-%m-%d').strftime('%d-%m-%Y'),center)
            sheet.write(row_id, 4,datetime.strptime(internclone.intern_id.date_of_birth_short,'%Y-%m-%d').strftime('%d-%m-%Y'),center)
            if internclone.intern_id.province:
                sheet.write(row_id, 5, internclone.intern_id.province.name, center)
            if internclone.intern_id.recruitment_employee:
                sheet.write(row_id, 6, internclone.intern_id.recruitment_employee.name, center)
            sheet.write(row_id, 7, '', center)
            # all_internclone = self.env['intern.internclone'].search([('intern_id','=',internclone.intern_id)])
            # invoices = []
            # for inte in all_internclone:
            #     invoices.append(inte.invoice_id)
            # interns_invoice = self.env['intern.invoice'].search([('id', 'in', invoices)])
            # interns_invoice = sorted(interns_invoice, key=lambda x: x.date_exam_short)
            #
            # for i,invoice in enumerate(interns_invoice):
            #     if i<3:
            #         sheet.write(row_id, 8+i, invoice.name, center)
            #     else:
            #         break
            sheet.write(row_id, 8, internclone.invoice_id.name, wrap)
            sheet.write(row_id, 9, '', center)
            sheet.write(row_id, 10, '', center)
            sheet.write(row_id, 11, internclone.reason_cancel_pass, wrap)
            row_id += 1
            counter +=1

        row_id += 1
        sheet.write(row_id, 1, u'Danh sách rút bỏ trúng tuyển', title_style)
        row_id += 2
        counter=1
        sheet.write(row_id, 0, u'STT', header_style)
        sheet.write(row_id, 1, u'Họ và tên', header_style)
        sheet.write(row_id, 2, u'Mã số', header_style)
        sheet.write(row_id, 3, u'Ngày nhập', header_style)
        sheet.write(row_id, 4, u'Năm sinh', header_style)
        sheet.write(row_id, 5, u'Quê quán', header_style)
        sheet.write(row_id, 6, u'Cán bộ tuyển dụng', header_style)
        sheet.write(row_id, 7, u'NĐ-Xí nghiệp', header_style)
        sheet.write(row_id, 8, u'TC lần 1', header_style)
        sheet.write(row_id, 9, u'TC lần 2', header_style)
        sheet.write(row_id, 10, u'TC lần 3', header_style)
        sheet.write(row_id, 11, u'Lý do rút bỏ', header_style)
        row_id += 1
        for internclone in interns_escape_exam:
            # intern = self.env['intern.intern'].browse(internclone.intern_id)
            sheet.write(row_id, 0, counter, center)
            sheet.write(row_id, 1, internclone.intern_id.name, center)
            sheet.write(row_id, 2, internclone.intern_id.custom_id, center)
            if internclone.intern_id.date_enter_source:
                sheet.write(row_id, 3, datetime.strptime(internclone.intern_id.date_enter_source, '%Y-%m-%d').strftime('%d-%m-%Y'), center)
            sheet.write(row_id, 4, datetime.strptime(internclone.intern_id.date_of_birth_short, '%Y-%m-%d').strftime('%d-%m-%Y'),
                        center)
            if internclone.intern_id.province:
                sheet.write(row_id, 5, internclone.intern_id.province.name, center)
            if internclone.intern_id.recruitment_employee:
                sheet.write(row_id, 6, internclone.intern_id.recruitment_employee.name, center)
            sheet.write(row_id, 7,'',center)
            # all_internclone = self.env['intern.internclone'].search([('intern_id', '=', internclone.intern_id)])
            # invoices = []
            # for inte in all_internclone:
            #     invoices.append(inte.invoice_id)
            # interns_invoice = self.env['intern.invoice'].search([('id', 'in', invoices)])
            # interns_invoice = sorted(interns_invoice, key=lambda x: x.date_exam_short)
            #
            # for i, invoice in enumerate(interns_invoice):
            #     if i < 3:
            #         sheet.write(row_id, 8 + i, invoice.name, center)
            #     else:
            #         break
            sheet.write(row_id, 8, internclone.invoice_id.name, wrap)
            sheet.write(row_id, 9, '', center)
            sheet.write(row_id, 10, '', center)
            sheet.write(row_id, 11, internclone.issues_reason, wrap)
            counter += 1
            row_id+=1

        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 18)
        sheet.set_column(2, 2, 10)
        sheet.set_column(3, 3, 12)
        sheet.set_column(4, 4, 12)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 18)
        sheet.set_column(7, 7, 10)
        sheet.set_column(8, 8, 20)
        sheet.set_column(11, 11, 25)


PhatSinhXlsx('report.intern.issue.xlsx','hoanghung.report')

class DepartureReport(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, reports):
        report_name = u'Báo cáo số lượng xuất cảnh trong tháng %s - %s'%(data['month'],data['year'])
        sheet = workbook.add_worksheet(report_name[:31])

        title_style = workbook.add_format({'bold': True})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        header_style = workbook.add_format(
            {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'fg_color': '#96b55e'})

        bold_no_border = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        wrap_no_border = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})

        row_id = 0
        sheet.write(row_id, 1, report_name, title_style)
        row_id += 3


        date_start_month = datetime.strptime('%s-%s-01'%(data['year'],data['month']),'%Y-%m-%d')

        internsclone = self.env['intern.internclone'].search([('departure','=',True),('date_departure','>=',date_start_month),('date_departure','<',date_start_month+relativedelta(months=1))])

        sheet.merge_range('C%d:D%d' % (row_id+1, row_id+1),u'Xuất cảnh', header_style)
        # sheet.write(row_id, 2, )
        sheet.write(row_id, 4, u'Hr.Group', header_style)
        sheet.write(row_id, 5, u'Bati.Group', header_style)
        sheet.write(row_id, 6, u'Hogamex', header_style)
        sheet.write(row_id, 7, u'Hoàng Hưng', header_style)
        sheet.write(row_id, 8, u'Tổng', header_style)

        row_id+=1
        for counter in range(1,13):
            sheet.write(row_id,2,counter,center)
            sheet.write(row_id,3,u'Tháng %d'%counter,center)
            sheet.write(row_id,4,'',center)
            sheet.write(row_id,5,'',center)
            sheet.write(row_id,6,'',center)
            if counter == int(data['month']):
                sheet.write(row_id, 7, len(internsclone), center)
                sheet.write(row_id, 8, len(internsclone), center)
            else:
                sheet.write(row_id, 7, '', center)
                sheet.write(row_id, 8, 0, center)
            row_id+=1
        sheet.merge_range('C%d:D%d' % (row_id+1, row_id+1),u'Tổng',header_style)
        sheet.write_formula('E17', '=SUM(E5:E16)',header_style)
        sheet.write_formula('F17', '=SUM(F5:F16)',header_style)
        sheet.write_formula('G17', '=SUM(G5:G16)',header_style)
        sheet.write_formula('H17', '=SUM(H5:H16)',header_style)
        sheet.write_formula('I17', '=SUM(I5:I16)',header_style)

        row_id+=2
        sheet.write(row_id,0,u'Bảng chi tiết',title_style)

        row_id+=2
        sheet.write(row_id,0,'TT',header_style)
        sheet.write(row_id,1,u'Họ và tên',header_style)
        sheet.write(row_id,2,u'Giới tính',header_style)
        sheet.write(row_id,3,u'Ngày sinh',header_style)
        sheet.write(row_id,4,u'Quê quán',header_style)
        sheet.write(row_id,5,u'Thời hạn HĐ',header_style)
        sheet.write(row_id,6,u'Ngày xuất cảnh',header_style)
        sheet.write(row_id,7,u'Ngành nghề',header_style)
        sheet.write(row_id,8,u'Pháp nhân',header_style)
        sheet.write(row_id,9,u'CB tuyển dụng',header_style)
        row_id+=1
        internsclone = sorted(internsclone,key=lambda x: x.invoice_id.id)
        for i,intern in enumerate(internsclone):
            sheet.write(row_id, 0, '%d'%(i+1), center)
            sheet.write(row_id, 1, u'%s'%intern.intern_id.name, wrap)
            if intern.intern_id.gender == 'nu':
                sheet.write(row_id, 2, u'Nữ', center)
            else:
                sheet.write(row_id, 2, u'Nam', center)
            sheet.write(row_id, 3, datetime.strptime(intern.intern_id.date_of_birth_short,'%Y-%m-%d').strftime('%d-%m-%Y'), center)
            sheet.write(row_id, 4, u'%s'%intern.intern_id.province.name, center)
            sheet.write(row_id, 5, u'%s năm'%intern.invoice_id.year_expire, center)
            sheet.write(row_id, 6, datetime.strptime(intern.date_departure,'%Y-%m-%d').strftime('%d-%m-%Y'), center)
            sheet.write(row_id, 7, u'%s'%intern.invoice_id.job_vi, header_style)
            if intern.invoice_id.dispatchcom1:
                sheet.write(row_id, 8, u'%s'%intern.invoice_id.dispatchcom1.name_short, center)
            else:
                sheet.write(row_id, 8, '',center)
            if intern.intern_id.recruitment_employee:
                sheet.write(row_id, 9, u'%s'%intern.intern_id.recruitment_employee.name, center)
            else:
                sheet.write(row_id, 8, '', center)

            row_id += 1


        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 18)
        sheet.set_column(2, 2, 10)
        sheet.set_column(3, 3, 12)
        sheet.set_column(4, 4, 12)
        sheet.set_column(5, 5, 12)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 20)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 18)

DepartureReport('report.intern.departure.xlsx', 'hoanghung.report')


class InternsPassReport(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, reports):

        report_name = u'Danh sách trúng tuyển tháng %s - %s' % (data['month'], data['year'])
        sheet = workbook.add_worksheet(report_name[:31])

        title_style = workbook.add_format({'bold': True})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap_right = workbook.add_format({'text_wrap': True, 'valign': 'vcenter', 'border': 1})
        header_style = workbook.add_format(
            {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'fg_color': '#96b55e'})

        bold_no_border = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        wrap_no_border = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})

        row_id = 0
        sheet.write(row_id, 2, report_name, title_style)
        row_id += 2

        sheet.write(row_id, 0, u'STT', header_style)
        sheet.write(row_id, 1, u'Họ và tên', header_style)
        sheet.write(row_id, 2, u'Giới tính', header_style)
        sheet.write(row_id, 3, u'Ngày sinh', header_style)
        sheet.write(row_id, 4, u'Quê quán', header_style)
        sheet.write(row_id, 5, u'Ngày trúng tuyển', header_style)
        sheet.write(row_id, 6, u'Đơn hàng', header_style)
        sheet.write(row_id, 7, u'Hạn HĐ', header_style)
        sheet.write(row_id, 8, u'Pháp nhân', header_style)
        row_id += 1
        date_start_month = datetime.strptime('%s-%s-01' % (data['year'], data['month']), '%Y-%m-%d')
        invoices = self.env['intern.invoice'].search([('hoso_created','!=',True),('status','>=',2),('status','<',4),('date_pass','>=',date_start_month),('date_pass','<',date_start_month + relativedelta(months=1))])

        intern_ids = []
        for invoice in invoices:
            intern_ids.extend(invoice.interns_pass_doc)

        for i,intern in enumerate(intern_ids):
            sheet.write(row_id, 0, u'%d'%(i+1), center)
            sheet.write(row_id, 1, u'%s'%intern.intern_id.name, center)
            if intern.intern_id.gender == 'nu':
                sheet.write(row_id, 2, u'Nữ', center)
            else:
                sheet.write(row_id, 2, u'Nam', center)
            sheet.write(row_id, 3,datetime.strptime(intern.intern_id.date_of_birth_short,'%Y-%m-%d').strftime('%d-%m-%Y'), center)
            sheet.write(row_id, 4, u'%s'%intern.intern_id.province.name, center)
            sheet.write(row_id, 5, datetime.strptime(intern.invoice_id.date_pass,'%Y-%m-%d').strftime('%d-%m-%Y'), center)
            sheet.write(row_id, 6, u'%s'%intern.invoice_id.name, wrap_right)
            sheet.write(row_id, 7, intern.invoice_id.year_expire, center)
            if intern.invoice_id.dispatchcom1:
                sheet.write(row_id, 8, u'%s'%intern.invoice_id.dispatchcom1.name_short, center)
            else:
                sheet.write(row_id, 8, u'', center)
            row_id+=1

        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 18)
        sheet.set_column(2, 2, 10)
        sheet.set_column(3, 3, 12)
        sheet.set_column(4, 4, 12)
        sheet.set_column(5, 5, 12)
        sheet.set_column(6, 6, 25)
        sheet.set_column(7, 7, 5)
        sheet.set_column(8, 8, 18)



InternsPassReport('report.interns.pass.xlsx', 'hoanghung.report')


class InternsNumberPassReport(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, reports):
        report_name = u'Báo cáo số lượng trúng tuyển đơn hàng tháng %s-%s' % (data['month'], data['year'])
        sheet = workbook.add_worksheet(report_name[:31])

        title_style = workbook.add_format({'bold': True})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap_right = workbook.add_format({'text_wrap': True, 'valign': 'vcenter', 'border': 1})
        header_style = workbook.add_format(
            {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'fg_color': '#96b55e'})

        bold_no_border = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        wrap_no_border = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})

        row_id = 0
        sheet.write(row_id, 2, report_name, title_style)

        row_id+=2
        sheet.merge_range('A%d:A%d' % (row_id+1, row_id+2),u'STT', header_style)
        sheet.merge_range('B%d:B%d'%(row_id+1, row_id+2),u'Tháng',header_style)

        sheet.merge_range('C%d:D%d'%(row_id+1, row_id+1),u'HR.Gr',header_style)
        sheet.write(row_id+1,2,u'3 năm',header_style)
        sheet.write(row_id+1,3,u'1 năm',header_style)
        sheet.merge_range('E%d:F%d' % (row_id + 1, row_id + 1), u'BATIMEX', header_style)
        sheet.write(row_id + 1, 4, u'3 năm', header_style)
        sheet.write(row_id + 1, 5, u'1 năm', header_style)
        sheet.merge_range('G%d:H%d' % (row_id + 1, row_id + 1), u'HOGAMEX', header_style)
        sheet.write(row_id + 1, 6, u'3 năm', header_style)
        sheet.write(row_id + 1, 7, u'1 năm', header_style)
        sheet.merge_range('I%d:J%d' % (row_id + 1, row_id + 1), u'HOÀNG HƯNG', header_style)
        sheet.write(row_id + 1, 8, u'3 năm', header_style)
        sheet.write(row_id + 1, 9, u'1 năm', header_style)

        date_start_month = datetime.strptime('%s-%s-01' % (data['year'], data['month']), '%Y-%m-%d')
        invoices_one = self.env['intern.invoice'].search(
            [('year_expire','=',1),('hoso_created', '!=', True), ('status', '>=', 2), ('status', '<', 4),
             ('date_pass', '>=', date_start_month), ('date_pass', '<', date_start_month + relativedelta(months=1))])

        count_pass_one = 0
        for invoice in invoices_one:
            count_pass_one+=len(invoice.interns_pass_doc)

        invoices_three = self.env['intern.invoice'].search(
            [('year_expire', '=', 3), ('hoso_created', '!=', True), ('status', '>=', 2), ('status', '<', 4),
             ('date_pass', '>=', date_start_month), ('date_pass', '<', date_start_month + relativedelta(months=1))])

        count_pass_three = 0
        for invoice in invoices_three:
            count_pass_three += len(invoice.interns_pass_doc)

        row_id+=2
        for i in range(1,13):
            sheet.write(row_id,0,i,center)
            sheet.write(row_id,1,u'Tháng %d'%i,center)
            sheet.write(row_id,2,'',center)
            sheet.write(row_id,3,'',center)
            sheet.write(row_id,4,'',center)
            sheet.write(row_id,5,'',center)
            sheet.write(row_id,6,'',center)
            sheet.write(row_id,7,'',center)
            if i == int(data['month']):
                sheet.write(row_id,8,count_pass_three,center)
                sheet.write(row_id,9,count_pass_one,center)
            else:
                sheet.write(row_id, 8, '', center)
                sheet.write(row_id, 9, '', center)
            row_id+=1
        sheet.merge_range('A%d:B%d' % (row_id + 1, row_id + 1), u'Tổng', header_style)
        sheet.write_formula('C%d'%(row_id+1),'=SUM(C%d:C%d)'%(row_id-11,row_id),header_style)
        sheet.write_formula('D%d'%(row_id+1),'=SUM(D%d:D%d)'%(row_id-11,row_id),header_style)
        sheet.write_formula('E%d'%(row_id+1),'=SUM(E%d:E%d)'%(row_id-11,row_id),header_style)
        sheet.write_formula('F%d'%(row_id+1),'=SUM(F%d:F%d)'%(row_id-11,row_id),header_style)
        sheet.write_formula('G%d'%(row_id+1),'=SUM(G%d:G%d)'%(row_id-11,row_id),header_style)
        sheet.write_formula('H%d'%(row_id+1),'=SUM(H%d:H%d)'%(row_id-11,row_id),header_style)
        sheet.write_formula('I%d'%(row_id+1),'=SUM(I%d:I%d)'%(row_id-11,row_id),header_style)
        sheet.write_formula('J%d'%(row_id+1),'=SUM(J%d:J%d)'%(row_id-11,row_id),header_style)

        row_id+=2
        sheet.write(row_id, 2, u'Báo cáo số lượng đơn hàng tháng %s-%s' % (data['month'], data['year']), title_style)
        row_id+=1
        sheet.merge_range('A%d:A%d' % (row_id+1, row_id+2),u'STT', header_style)
        sheet.merge_range('B%d:B%d'%(row_id+1, row_id+2),u'Tháng',header_style)

        sheet.merge_range('C%d:D%d'%(row_id+1, row_id+1),u'HR.Gr',header_style)
        sheet.write(row_id+1,2,u'3 năm',header_style)
        sheet.write(row_id+1,3,u'1 năm',header_style)
        sheet.merge_range('E%d:F%d' % (row_id + 1, row_id + 1), u'BATIMEX', header_style)
        sheet.write(row_id + 1, 4, u'3 năm', header_style)
        sheet.write(row_id + 1, 5, u'1 năm', header_style)
        sheet.merge_range('G%d:H%d' % (row_id + 1, row_id + 1), u'HOGAMEX', header_style)
        sheet.write(row_id + 1, 6, u'3 năm', header_style)
        sheet.write(row_id + 1, 7, u'1 năm', header_style)
        sheet.merge_range('I%d:J%d' % (row_id + 1, row_id + 1), u'HOÀNG HƯNG', header_style)
        sheet.write(row_id + 1, 8, u'3 năm', header_style)
        sheet.write(row_id + 1, 9, u'1 năm', header_style)
        row_id += 2
        for i in range(1, 13):
            sheet.write(row_id, 0, i, center)
            sheet.write(row_id, 1, u'Tháng %d' % i, center)
            sheet.write(row_id, 2, '', center)
            sheet.write(row_id, 3, '', center)
            sheet.write(row_id, 4, '', center)
            sheet.write(row_id, 5, '', center)
            sheet.write(row_id, 6, '', center)
            sheet.write(row_id, 7, '', center)
            if i == int(data['month']):
                sheet.write(row_id, 8, len(invoices_three), center)
                sheet.write(row_id, 9, len(invoices_one), center)
            else:
                sheet.write(row_id, 8, '', center)
                sheet.write(row_id, 9, '', center)
            row_id += 1




InternsNumberPassReport('report.interns.numberpass.xlsx', 'hoanghung.report')


class InvoicePauseStopReport(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, reports):
        report_name = u'Danh sách đơn hàng hoãn-huỷ thi tuyển tháng %s-%s' % (data['month'], data['year'])
        sheet = workbook.add_worksheet(report_name[:31])

        title_style = workbook.add_format({'bold': True})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap_right = workbook.add_format({'text_wrap': True, 'valign': 'vcenter', 'border': 1})
        header_style = workbook.add_format(
            {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'fg_color': '#96b55e'})

        bold_no_border = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        wrap_no_border = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        center_no_border = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

        row_id = 0
        sheet.write(row_id, 2, u'SỐ LƯỢNG ĐƠN HÀNG HOÃN - HUỶ', title_style)
        row_id += 2
        sheet.write(row_id,1,'STT',header_style)
        sheet.write(row_id,2,u'Tháng',header_style)
        sheet.write(row_id,3,u'HR.Gr',header_style)
        sheet.write(row_id,4,u'BATIMEX',header_style)
        sheet.write(row_id,5,u'HOGAMEX',header_style)
        sheet.write(row_id,6,u'HOÀNG HƯNG',header_style)
        row_id+=1
        date_start_month = datetime.strptime('%s-%s-01' % (data['year'], data['month']), '%Y-%m-%d')
        # datetime_start_month = datetime.strptime('%s-%s-01 00:00:00' % (data['year'], data['month']), '%Y-%m-%d %H:%M:%S')
        invoices_pause = self.env['intern.invoice'].search([('status','=',6),('date_pause_cancel_exam','!=',False),('date_pass','!=',False),('date_pause_cancel_exam','>=',date_start_month.strftime("%Y-%m-%d %H:%M:%S")),('date_pass', '<',date_start_month + relativedelta(months=1))])
        invoices_stop = self.env['intern.invoice'].search([('status','=',7),('date_pause_cancel_exam','!=',False),('date_pass','!=',False),('date_pause_cancel_exam','>=',date_start_month.strftime("%Y-%m-%d %H:%M:%S")),('date_pass', '<' ,date_start_month + relativedelta(months=1))])
        for i in range(1,12):
            sheet.write(row_id, 1, '%d'%i, center)
            sheet.write(row_id, 2, u'Tháng %d'%i, center)
            sheet.write(row_id, 3, '', center)
            sheet.write(row_id, 4, '', center)
            sheet.write(row_id, 5, '', center)
            if i != int(data['month']):
                sheet.write(row_id, 6, '', center)
            else:
                sheet.write(row_id, 6, '%d'%(len(invoices_pause)+len(invoices_stop)), center)
            row_id+=1
        row_id+=1
        sheet.merge_range('A%d:D%d'%(row_id+1,row_id+1),u'Danh sách chi tiết',wrap_no_border)
        row_id+=1
        sheet.write(row_id,4,u'DANH SÁCH ĐƠN HÀNG HOÃN - HUỶ THI TUYỂN THÁNG %s/%s'%(data['month'],data['year']),center_no_border)
        row_id+=1
        sheet.write(row_id,0,'STT',header_style)
        sheet.write(row_id,1,u'TÊN ĐƠN HÀNG',header_style)
        sheet.write(row_id,2,u'NGÀY THI TUYỂN',header_style)
        sheet.write(row_id,3,u'SL trúng tuyển',header_style)
        sheet.write(row_id,4,u'SL tham gia thi tuyển',header_style)
        sheet.write(row_id,5,u'CÔNG TY (Phòng PTTT)',header_style)
        sheet.write(row_id,6,u'LÝ DO',header_style)
        row_id+=1
        sheet.merge_range('H%d:H%d'%(row_id,row_id+1),u'(DS chốt thi tuyển, TTS xuống học thi tuyển)',header_style)
        row_id+=1
        sheet.merge_range('A%d:G%d'%(row_id,row_id),u'ĐƠN HÀNG HOÃN THI TUYỂN (LÙI NGÀY THI)',header_style)
        for i,invoice in enumerate(invoices_pause):
            sheet.write(row_id,0,'%d'%(i+1),center)
            sheet.write(row_id,1,u'%s'%invoice.name,center)
            if invoice.date_exam_short:
                sheet.write(row_id,2,datetime.strptime(invoice.date_exam_short,'%Y-%m-%d').strftime('%d-%m-%Y'),center)
            else:
                sheet.write(row_id, 2, '', center)
            sheet.write(row_id,3,'%d'%invoice.number_total,center)
            sheet.write(row_id,4,'%d'%invoice.source_total,center)
            if invoice.room_pttt:
                sheet.write(row_id,5,'%s'%invoice.room_pttt.name)
            else:
                sheet.write(row_id, 5, '', center)
            sheet.write(row_id, 6, '', center)
            sheet.write(row_id, 7, '', center)
            row_id+=1
        if len(invoices_pause)<3:
            for i in range(len(invoices_pause),4):
                sheet.write(row_id, 0, '', center)
                sheet.write(row_id, 1, '', center)
                sheet.write(row_id, 2, '', center)
                sheet.write(row_id, 3, '', center)
                sheet.write(row_id, 4, '', center)
                sheet.write(row_id, 5, '', center)
                sheet.write(row_id, 6, '', center)
                sheet.write(row_id, 7, '', center)
                row_id+=1
        sheet.merge_range('A%d:B%d'%(row_id+1,row_id+1),u'TỔNG',center)
        sheet.write(row_id,2,'',center)
        sheet.write_formula('D%d'%(row_id+1),'=SUM(D%d:D%d)'%(row_id-max(3, len(invoices_pause)),row_id-1),center)
        sheet.write_formula('E%d'%(row_id+1),'=SUM(E%d:E%d)'%(row_id-max(3, len(invoices_pause)),row_id-1),center)
        sheet.write_formula('F%d'%(row_id+1),'=SUM(F%d:F%d)'%(row_id-max(3, len(invoices_pause)),row_id-1),center)
        sheet.write(row_id, 5, '', center)
        sheet.write(row_id, 6, '', center)
        sheet.write(row_id, 7, '', center)
        row_id += 1

        sheet.merge_range('A%d:G%d' % ((row_id+1), (row_id+1)), u'ĐƠN HÀNG HUỶ THI TUYỂN',header_style)
        sheet.write(row_id, 7, '', header_style)
        row_id += 1
        counter=0
        for i,invoice in enumerate(invoices_stop):
            if not invoice.date_pause_cancel_exam or not invoice.date_exam_short or datetime.strptime(invoice.date_pause_cancel_exam) < datetime.strptime(invoice.date_exam_short):
                sheet.write(row_id,0,'%d'%(i+1),center)
                sheet.write(row_id,1,u'%s'%invoice.name,center)
                if invoice.date_exam_short:
                    sheet.write(row_id,2,datetime.strptime(invoice.date_exam_short,'%Y-%m-%d').strftime('%d-%m-%Y'),center)
                else:
                    sheet.write(row_id, 2, '', center)
                sheet.write(row_id,3,'%d'%invoice.number_total,center)
                sheet.write(row_id,4,'%d'%invoice.source_total,center)
                if invoice.room_pttt:
                    sheet.write(row_id,5,'%s'%invoice.room_pttt.name, center)
                else:
                    sheet.write(row_id, 5, '', center)
                sheet.write(row_id, 6, '', center)
                sheet.write(row_id, 7, '', center)
                row_id+=1
                counter+=1
        if counter<3:
            for i in range(counter,4):
                sheet.write(row_id, 0, '', center)
                sheet.write(row_id, 1, '', center)
                sheet.write(row_id, 2, '', center)
                sheet.write(row_id, 3, '', center)
                sheet.write(row_id, 4, '', center)
                sheet.write(row_id, 5, '', center)
                sheet.write(row_id, 6, '', center)
                sheet.write(row_id, 7, '', center)
                row_id+=1
        sheet.merge_range('A%d:B%d'%(row_id+1,row_id+1),u'TỔNG',center)
        sheet.write(row_id,2,'',center)
        sheet.write_formula('D%d'%(row_id+1),'=SUM(D%d:D%d)'%(row_id-max(3, counter),row_id-1),center)
        sheet.write_formula('E%d'%(row_id+1),'=SUM(E%d:E%d)'%(row_id-max(3, counter),row_id-1),center)
        sheet.write_formula('F%d'%(row_id+1),'=SUM(F%d:F%d)'%(row_id-max(3, counter),row_id-1),center)
        sheet.write(row_id, 5, '', center)
        sheet.write(row_id, 6, '', center)
        sheet.write(row_id, 7, '', center)
        row_id+=1
        sheet.merge_range('A%d:G%d' % (row_id+1, row_id+1), u'ĐƠN HÀNG THI TUYỂN XONG HUỶ KHÔNG LẤY AI', header_style)
        sheet.write(row_id, 7, '', header_style)
        row_id += 1
        counter = 0
        for i, invoice in enumerate(invoices_stop):
            if not invoice.date_pause_cancel_exam or not invoice.date_exam_short or datetime.strptime(
                    invoice.date_pause_cancel_exam) < datetime.strptime(invoice.date_exam_short):
                continue
            else:
                sheet.write(row_id, 0, '%d' % (i + 1), center)
                sheet.write(row_id, 1, u'%s' % invoice.name, center)
                if invoice.date_exam_short:
                    sheet.write(row_id, 2, datetime.strptime(invoice.date_exam_short, '%Y-%m-%d').strftime('%d-%m-%Y'),
                                center)
                else:
                    sheet.write(row_id, 2, '', center)
                sheet.write(row_id, 3, '%d' % invoice.number_total, center)
                sheet.write(row_id, 4, '%d' % invoice.source_total, center)
                if invoice.room_pttt:
                    sheet.write(row_id, 5, '%s' % invoice.room_pttt.name, center)
                else:
                    sheet.write(row_id, 5, '', center)
                sheet.write(row_id, 6, '', center)
                sheet.write(row_id, 7, '', center)
                row_id += 1
                counter += 1
        if counter < 3:
            for i in range(counter, 4):
                sheet.write(row_id, 0, '', center)
                sheet.write(row_id, 1, '', center)
                sheet.write(row_id, 2, '', center)
                sheet.write(row_id, 3, '', center)
                sheet.write(row_id, 4, '', center)
                sheet.write(row_id, 5, '', center)
                sheet.write(row_id, 6, '', center)
                sheet.write(row_id, 7, '', center)
                row_id += 1
        sheet.merge_range('A%d:B%d' % (row_id+1, row_id+1), u'TỔNG', center)
        sheet.write(row_id, 2, '', center)
        sheet.write_formula('D%d' % (row_id+1), '=SUM(D%d:D%d)' % (row_id - max(3, counter), row_id - 1), center)
        sheet.write_formula('E%d' % (row_id+1), '=SUM(E%d:E%d)' % (row_id - max(3, counter), row_id - 1), center)
        sheet.write_formula('F%d' % (row_id+1), '=SUM(F%d:F%d)' % (row_id - max(3, counter), row_id - 1), center)
        sheet.write(row_id, 5, '', center)
        sheet.write(row_id, 6, '', center)
        sheet.write(row_id, 7, '', center)


        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 18)
        sheet.set_column(2, 2, 13)
        sheet.set_column(3, 3, 13)
        sheet.set_column(4, 4, 13)
        sheet.set_column(5, 5, 13)
        sheet.set_column(6, 6, 13)
        sheet.set_column(7, 7, 25)

InvoicePauseStopReport('report.invoice.pausestop.xlsx', 'hoanghung.report')


class DepositReport(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, reports):
        report_name = u'Nộp cọc ngày %s'%(datetime.today().strftime('%d-%m-%Y'))

        title_style = workbook.add_format({'bold': True})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap_right = workbook.add_format({'text_wrap': True, 'valign': 'vcenter', 'border': 1})
        header_style = workbook.add_format(
            {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'fg_color': '#96b55e'})

        bold_no_border = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        wrap_no_border = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        center_no_border = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
        money = workbook.add_format({'num_format': '#,###', 'border': 1})

        sheet = workbook.add_worksheet(report_name[:31])

        row_id = 0
        sheet.write(row_id,0,'STT',header_style)
        sheet.write(row_id,1,u'Họ tên TTS',header_style)
        sheet.write(row_id,2,u'Ngày sinh',header_style)
        sheet.write(row_id,3,u'CMND/thẻ CC',header_style)
        sheet.write(row_id,4,u'Tỉnh/TP',header_style)
        sheet.write(row_id,5,u'Cán bộ nộp cọc',header_style)
        sheet.write(row_id,6,u'Cán bộ nhập',header_style)
        sheet.write(row_id,7,u'Tiền cọc',header_style)
        sheet.write(row_id,8,u'Thời gian',header_style)
        row_id+=1
        # _logger.info("DATE %s"%datetime.today())
        start_date = datetime.strptime('%s 00:00:00'%datetime.today().strftime('%Y-%m-%d'),'%Y-%m-%d %H:%M:%S')
        tomorrow_date = start_date + relativedelta(days=1)
        _logger.info("START DATE %s %s "%(start_date.strftime("%Y-%m-%d %H:%M:%S"),tomorrow_date.strftime("%Y-%m-%d %H:%M:%S")))
        logdeposits = self.env['intern.deposit.history'].search([('create_date','>=',start_date.strftime("%Y-%m-%d %H:%M:%S")),('create_date','<',tomorrow_date.strftime("%Y-%m-%d %H:%M:%S")),('have_deposit','=',True)])

        for i,log in enumerate(logdeposits):
            sheet.write(row_id,0, i+1,center)
            sheet.write(row_id,1, u'%s'%log.intern_id.name,center)
            if log.intern_id.date_of_birth_short:
                sheet.write(row_id,2, datetime.strptime(log.intern_id.date_of_birth_short,'%Y-%m-%d').strftime('%d/%m/%Y'),center)
            else:
                sheet.write(row_id, 2, '',center)
            sheet.write(row_id,3, log.intern_id.cmnd_or_tcc,center)
            sheet.write(row_id,4, log.intern_id.province.name,center)
            if log.employee_deposit:
                sheet.write(row_id,5, log.employee_deposit.name,center)
            else:
                sheet.write(row_id, 5, '', center)
            sheet.write(row_id,6, log.create_uid.name,center)
            sheet.write(row_id, 7,log.money_deposit, money)
            sheet.write(row_id, 8,(datetime.strptime(log.create_date, '%Y-%m-%d %H:%M:%S') + relativedelta(hours=7)).strftime('%d/%m/%Y %H:%M'), money)
            row_id+=1
        sheet.write(row_id,6,u'Tổng',center)
        sheet.write_formula('H%d'% (row_id+1), '=SUM(H%d:H%d)' % (row_id - len(logdeposits)+1, row_id ), money)

        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 18)
        sheet.set_column(2, 2, 13)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 13)
        sheet.set_column(5, 5, 18)
        sheet.set_column(6, 6, 18)
        sheet.set_column(7, 7, 13)
        sheet.set_column(8, 8, 15)

        report_name = u'Rút cọc ngày %s' % (datetime.today().strftime('%d-%m-%Y'))
        sheet_withdraw = workbook.add_worksheet(report_name[:31])

        row_id = 0
        sheet_withdraw.write(row_id, 0, 'STT', header_style)
        sheet_withdraw.write(row_id, 1, u'Họ tên TTS', header_style)
        sheet_withdraw.write(row_id, 2, u'Ngày sinh', header_style)
        sheet_withdraw.write(row_id, 3, u'CMND/thẻ CC', header_style)
        sheet_withdraw.write(row_id, 4, u'Tỉnh/TP', header_style)
        sheet_withdraw.write(row_id, 5, u'Cán bộ rút cọc', header_style)
        sheet_withdraw.write(row_id, 6, u'Cán bộ nhập', header_style)
        sheet_withdraw.write(row_id, 7, u'Tiền cọc', header_style)
        row_id += 1
        # start_date = datetime.strptime('%s 00:00:00' % data['start_date'], '%Y-%m-%d %H:%M:%S')
        # tomorrow_date = start_date + relativedelta(days=1)
        # _logger.info("START DATE %s %s " % (
        # start_date.strftime("%Y-%m-%d %H:%M:%S"), tomorrow_date.strftime("%Y-%m-%d %H:%M:%S")))
        logdeposits = self.env['intern.deposit.history'].search(
            [('create_date', '>=', start_date.strftime("%Y-%m-%d %H:%M:%S")),
             ('create_date', '<', tomorrow_date.strftime("%Y-%m-%d %H:%M:%S")), ('have_deposit', '=', False)])

        for i, log in enumerate(logdeposits):
            sheet_withdraw.write(row_id, 0, i + 1, center)
            sheet_withdraw.write(row_id, 1, u'%s' % log.intern_id.name, center)
            if log.intern_id.date_of_birth_short:
                sheet_withdraw.write(row_id, 2,
                            datetime.strptime(log.intern_id.date_of_birth_short, '%Y-%m-%d').strftime('%d/%m/%Y'),
                            center)
            else:
                sheet_withdraw.write(row_id, 2, '', center)
            sheet_withdraw.write(row_id, 3, log.intern_id.cmnd_or_tcc, center)
            sheet_withdraw.write(row_id, 4, log.intern_id.province.name, center)
            if log.employee_withdraw:
                sheet_withdraw.write(row_id, 5, log.employee_withdraw.name, center)
            else:
                sheet_withdraw.write(row_id, 5, '', center)
            sheet_withdraw.write(row_id, 6, log.create_uid.name, center)
            sheet_withdraw.write(row_id, 7, log.money_deposit, money)
            sheet.write(row_id, 8,
                        (datetime.strptime(log.create_date, '%Y-%m-%d %H:%M:%S') + relativedelta(hours=7)).strftime(
                            '%d/%m/%Y %H:%M'), money)
            row_id += 1

        sheet_withdraw.write(row_id, 6, u'Tổng', center)
        sheet_withdraw.write_formula('H%d' % (row_id + 1), '=SUM(H%d:H%d)' % (row_id - len(logdeposits)+1, row_id ), money)

        sheet_withdraw.set_column(0, 0, 5)
        sheet_withdraw.set_column(1, 1, 18)
        sheet_withdraw.set_column(2, 2, 13)
        sheet_withdraw.set_column(3, 3, 15)
        sheet_withdraw.set_column(4, 4, 13)
        sheet_withdraw.set_column(5, 5, 18)
        sheet_withdraw.set_column(6, 6, 18)
        sheet_withdraw.set_column(7, 7, 13)
        sheet_withdraw.set_column(8, 8, 15)

DepositReport('report.intern.deposit.xlsx', 'hoanghung.report')


class CoCheDonHangReport(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, reports):
        report_name = u'Bảng cơ chế đơn hàng tháng %s năm %s' % (data['month'], data['year'])
        title_style = workbook.add_format({'bold': True})
        title_style.set_font_size(18)
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap_right = workbook.add_format({'text_wrap': True, 'valign': 'vcenter', 'border': 1})
        header_style = workbook.add_format(
            {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'fg_color': '#96b55e'})

        bold_no_border = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        wrap_no_border = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})
        center_no_border = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
        money = workbook.add_format({'num_format': '#.##0', 'border': 1})

        sheet = workbook.add_worksheet(report_name[:31])
        row_id = 0

        sheet.write(row_id,6,report_name,title_style)
        row_id +=2
        sheet.merge_range('A%d:A%d'%(row_id+1,row_id+2),'STT', header_style)
        sheet.merge_range('B%d:B%d'%(row_id+1,row_id+2), u'Đơn hàng/Công việc cụ thể', header_style)
        sheet.merge_range('C%d:C%d'%(row_id+1,row_id+2), u'Loại hợp đồng', header_style)
        sheet.merge_range('D%d:D%d'%(row_id+1,row_id+2), u'CB PTTT', header_style)
        sheet.merge_range('E%d:E%d'%(row_id+1,row_id+2), u'Phòng', header_style)
        sheet.merge_range('F%d:F%d'%(row_id+1,row_id+2), u'Địa điểm làm việc', header_style)
        sheet.merge_range('G%d:H%d'%(row_id+1,row_id+1),u'Số lượng trúng tuyển', header_style)
        sheet.merge_range('I%d:I%d' % (row_id+1,row_id+2), u'Số form dự thi', header_style)
        sheet.merge_range('J%d:J%d' % (row_id+1,row_id+2), u'Phí XC', header_style)
        sheet.merge_range('K%d:K%d' % (row_id+1,row_id+2), u'Cơ chế cho CBTD', header_style)
        sheet.merge_range('L%d:L%d' % (row_id+1,row_id+2), u'Ngày thi', header_style)
        sheet.merge_range('M%d:M%d' % (row_id+1,row_id+2), u'Mức lương cơ bản (Yên)', header_style)
        sheet.merge_range('N%d:N%d' % (row_id+1,row_id+2), u'Mức lương thực lĩnh Chưa tính làm thêm (Yên)', header_style)
        sheet.merge_range('O%d:Q%d' % (row_id+1,row_id+1), u'Yêu cầu', header_style)
        row_id+=1
        sheet.write(row_id, 6, u'Nam', header_style)
        sheet.write(row_id, 7, u'Nữ', header_style)
        sheet.write(row_id, 14, u'Tuổi', header_style)
        sheet.write(row_id, 15, u'Trình độ', header_style )
        sheet.write(row_id, 16, u'Khác', header_style)

        row_id+=1
        date_start_month = datetime.strptime('%s-%s-01' % (data['year'], data['month']), '%Y-%m-%d')
        invoices = self.env['intern.invoice'].search([('date_exam_short','>=',date_start_month),('date_exam_short','<',date_start_month + relativedelta(months=1))])
        for i,invoice in enumerate(invoices):
            sheet.write(row_id,0,i+1,center)
            sheet.write(row_id,1,u'%s'%invoice.name,center)
            sheet.write(row_id,2,invoice.year_expire,center)
            if invoice.employee_pttt:
                sheet.write(row_id,3,invoice.employee_pttt.name,center)
            else:
                sheet.write(row_id, 3,'', center)
            if invoice.room_pttt:
                sheet.write(row_id,4,invoice.room_pttt.name,center)
            else:
                sheet.write(row_id, 4,'', center)
            sheet.write(row_id,5,invoice.place_to_work,wrap)
            sheet.write(row_id,6,invoice.number_man,center)
            sheet.write(row_id,7,invoice.number_women,center)
            sheet.write(row_id,8,invoice.source_total,center)
            phixc = ''
            if invoice.fee_departure:
                phixc += '%d'%invoice.fee_departure
            if invoice.fee_departure_women:
                if invoice.fee_departure:
                    phixc += u'(nam)/'
                phixc += '%d'%invoice.fee_departure_women
                if invoice.fee_departure:
                    phixc += u'(nữ)'
            sheet.write(row_id,9,phixc,wrap)

            coche = ''
            if invoice.count_target:
                coche+= u'Thưởng %s/Tính chỉ tiêu mới'%invoice.bonus_target
            if invoice.count_target_women:
                if invoice.count_target:
                    coche+= u'(nam)/'
                coche += u'Thưởng %s/Tính chỉ tiêu mới' % invoice.bonus_target_women
                if invoice.count_target:
                    coche+= u'(nữ)'
            sheet.write(row_id, 10,coche,wrap)

            sheet.write(row_id,11, datetime.strptime(invoice.date_exam_short,'%Y-%m-%d').strftime('%d-%m-%Y'),center)
            sheet.write(row_id,12, invoice.salary_base, center)
            sheet.write(row_id,13, invoice.salary_real, center)
            sheet.write(row_id,14, '%d-%d'%(invoice.age_from,invoice.age_to), center)
            if invoice.certificate:
                sheet.write(row_id, 15, '%s'%invoice.certificate.name_in_vn[len(u'Bằng tốt nghiệp '):],center)
            else:
                sheet.write(row_id, 15, '',center)
            if invoice.other_requirement:
                sheet.write(row_id,16,invoice.other_requirement,wrap)
            else:
                sheet.write(row_id, 16, '', wrap)
            row_id+=1

        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 5)
        sheet.set_column(3, 3, 18)
        sheet.set_column(4, 4, 8)
        sheet.set_column(5, 5, 12)
        sheet.set_column(6, 6, 6)
        sheet.set_column(7, 7, 6)
        sheet.set_column(8, 8, 6)
        sheet.set_column(9, 9, 13)
        sheet.set_column(10, 10, 13)
        sheet.set_column(11, 11, 13)
        sheet.set_column(12, 12, 10)
        sheet.set_column(13, 13, 10)
        sheet.set_column(14, 14, 10)
        sheet.set_column(15, 15, 10)
        sheet.set_column(16, 16, 20)



CoCheDonHangReport('report.invoice.coche.xlsx', 'hoanghung.report')