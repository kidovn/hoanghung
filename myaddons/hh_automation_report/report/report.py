# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.addons.hh_intern.models import intern_utils
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
import time
from sets import Set
import logging
_logger = logging.getLogger(__name__)

class InternExamReportAnnounce(models.AbstractModel):
    _name = 'report.hh_automation_report.report_intern_exam_view'

    @api.multi
    def render_html(self, docids, data=None):
        _logger.info("DOcids %s"%docids)
        invoice = self.env['intern.invoice'].browse(docids[0])


        # list_code = []
        # list_code_prepare = []
        # has_prepare = False
        interns = sorted(invoice.interns_exam_doc, key=lambda l: l[0].sequence_exam)

        interns_nam = []
        interns_nu = []

        for intern in interns:
            if intern.gender == 'nu':
                interns_nu.append(intern)
            else:
                interns_nam.append(intern)


        # today = intern_utils.date_time_in_vn_lower(datetime.today().day,datetime.today().month,datetime.today().year)
        docargs = {
            'record': invoice,
            'interns_nam':interns_nam,
            'interns_nu':interns_nu,
            'nam_size':len(interns_nam),
            'nu_size':len(interns_nu)
            # 'codes':list_code,
            # 'has_prepare':has_prepare,
            # 'today':today
        }
        return self.env['report'].render('hh_automation_report.report_intern_exam_view', values=docargs)


class TargetHuntReport(models.TransientModel):
    _name = 'hoanghung.report'

    start_date = fields.Date('Ngày bắt đầu', default=time.strftime('%Y-%m-01'))
    end_date = fields.Date('Ngày kết thúc', default=fields.Date.today)

    month = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                              ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                              ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    @api.model
    def _get_current_year(self):
        return str(datetime.today().year)

    def print_xls_report(self):
        data = self.read()[0]
        report_id = self._context['active_id']
        report = self.env['hh.actionreport'].browse(report_id)
        return {'type': 'ir.actions.report.xml',
                'report_name': report.report_type.report_name,
                'datas': data
                }


class TargetHuntReportXlsx(ReportXlsx):
    def convert_to_vn_date(self,date_string):
        if date_string:
            return datetime.strftime(datetime.strptime(date_string, '%Y-%m-%d'),'%d-%m-%Y')
        else:
            return None
    def generate_xlsx_report(self, workbook, data, objects):
        # _logger.info("TEST")
        # One sheet by partner
        sheet = workbook.add_worksheet(u'Bảng chỉ tiêu khối tuyển dụng')
        title_style = workbook.add_format({'bold': True})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        header_style = workbook.add_format(
            {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'fg_color': '#96b55e'})

        row_id = 0
        sheet.write(row_id,3,u'Bảng chỉ tiêu khối tuyển dụng',title_style)
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 18)
        # sheet.set_column(3, 3, 12)
        # sheet.set_column(4, 4, 15)


        sheet.write(row_id, 0, u'STT', header_style)
        sheet.write(row_id, 1, u'Họ và tên', header_style)
        sheet.write(row_id, 2, u'Giới tính', header_style)
        sheet.write(row_id, 3, u'Mã số', header_style)
        sheet.write(row_id, 4, u'Năm sinh', header_style)
        sheet.write(row_id, 5, u'Quê quán', header_style)
        sheet.write(row_id, 6, u'CBTD', header_style)
        sheet.write(row_id, 7, u'Phòng TD', header_style)
        sheet.write(row_id, 8, u'Chỉ tiêu', header_style)
        sheet.write(row_id, 9, u'Tiến cử lần 1', header_style)
        sheet.write(row_id, 10, u'Tiến cử lần 2', header_style)
        sheet.write(row_id, 11, u'Tiến cử lần 3', header_style)
        sheet.write(row_id, 12, u'Tiến cử lần 4', header_style)
        sheet.write(row_id, 13, u'Tiến cử lần 5', header_style)
        row_id += 1

        # self.env['intern.invoice'].read_group(domains, fields, tmp_groupbys, lazy=False)
        invoices = self.env['intern.invoice'].search([('date_exam_short','>=',data['start_date']),('date_exam_short','<=',data['end_date'])])
        intern_entersource = self.env['intern.intern'].search([('gender','=','nu'),('enter_source','=','2'),('date_enter_source','>=',data['start_date']),('date_enter_source','<=',data['end_date'])])

        list_interns = Set([])
        for invoice in invoices:
            for intern in invoice.interns_clone:
                if intern.confirm_exam and not intern.cancel_exam:
                    list_interns.add(intern.intern_id.id)
        for intern in intern_entersource:
            list_interns.add(intern.id)

        # interns = self.env['intern.intern'].search([('id','in',list(list_interns))])
        interns = self.env['intern.intern'].browse(list(list_interns))
        # interns.read()

        def get_room_recuitment(x):
            if x.room_recruitment:
                return x.room_recruitment.name
            else:
                return None
        def get_employee_recuitment(x):
            if x.recruitment_employee:
                return x.recruitment_employee.name
            else:
                return None

        interns = sorted(interns,key=lambda x: (get_room_recuitment(x),get_employee_recuitment(x)))

        for i,intern in enumerate(interns):
            # intern.read()
            sheet.write(row_id, 0, u'%d'%(i+1), wrap)
            sheet.write(row_id, 1, u'%s'%intern.name, wrap)
            if intern.gender == 'nu':
                sheet.write(row_id, 2, u'Nữ', wrap)
            else:
                sheet.write(row_id, 2, u'Nam', wrap)
            sheet.write(row_id, 3, u'%s'%intern.custom_id, wrap)
            sheet.write(row_id, 4, u'%s' % self.convert_to_vn_date(intern.date_of_birth_short), wrap)
            sheet.write(row_id, 5, u'%s'%intern.province.name, wrap)
            sheet.write(row_id, 6, u'%s'%intern.recruitment_employee.name, wrap)
            sheet.write(row_id, 7, u'%s'%intern.room_recruitment.name, wrap)
            internsclone = self.env['intern.internclone'].search([('intern_id','=',intern.id),('confirm_exam','=',True),('cancel_exam','=',False)])
            invoice_ids = []
            for iter in internsclone:
                invoice_ids.append(iter.invoice_id.id)
            interns_invoice = self.env['intern.invoice'].search([('id','in',invoice_ids),('date_exam_short','!=',False),('status','<=',3)])
            interns_invoice = sorted(interns_invoice,key=lambda x: x.date_exam_short)


            #Tinh chi tieu
            count_nh = 0
            count_dh = 0
            add_five = False
            start_date = datetime.strptime(data['start_date'],'%Y-%m-%d')
            end_date = datetime.strptime(data['end_date'],'%Y-%m-%d')
            for i, invoice in enumerate(interns_invoice):
                date_exam = datetime.strptime(invoice.date_exam_short,'%Y-%m-%d')
                if date_exam >= start_date and date_exam <= end_date:
                    if intern.gender == 'nu':
                        if intern.enter_source == '2':
                            date_enter_source = datetime.strptime(intern.date_enter_source, '%Y-%m-%d')


                            if date_enter_source <= date_exam:
                                if i == 0:
                                    continue
                                elif date_enter_source >= datetime.strptime(interns_invoice[i-1].date_exam_short, '%Y-%m-%d'):
                                    continue
                                else:
                                    if invoice.job_vi and 'May ' in invoice.job_vi:
                                        count_dh+=1
                                    else:
                                        count_nh+=1
                        else:
                            if invoice.job_vi and 'May ' in invoice.job_vi:
                                count_dh += 1
                            else:
                                count_nh += 1

                    else:
                        if i == 0:
                            count_nh+=1

                        elif invoice.count_target:
                            count_nh+=1


            if intern.gender == 'nu' and intern.enter_source == '2':
                date_enter_source = datetime.strptime(intern.date_enter_source,'%Y-%m-%d')
                if start_date <= date_enter_source and date_enter_source <= end_date:
                    count_dh +=1

            chi_tieu = ''
            if count_nh>0:
                chi_tieu+='%d NH'%count_nh
                if count_dh>0:
                    chi_tieu+=', '
            if count_dh>0:
                chi_tieu+='%d DH'%count_dh

            sheet.write(row_id, 8, chi_tieu, wrap)

            #write cac don hang

            if intern.enter_source == '2':
                counter = 0
                has_entered = False
                date_enter_source = datetime.strptime(intern.date_enter_source,'%Y-%m-%d')
                pos_enter_source = 9
                for i,invoice in enumerate(interns_invoice):
                    if date_enter_source< datetime.strptime(invoice.date_exam_short,'%Y-%m-%d'):
                        break
                    pos_enter_source = 10+i

                for x in range(9,14):
                    if x == pos_enter_source:
                        sheet.write(row_id, x, u'DH T%d'%date_enter_source.month, wrap)
                        continue
                    if counter<len(interns_invoice):
                        # if not has_entered and (not intern.date_enter_source or date_enter_source <  datetime.strptime(interns_invoice[counter].date_exam_short,'%Y-%m-%d')):
                        #     sheet.write(row_id, x, u'DH', wrap)
                        #     has_entered = True
                        # else:
                        sheet.write(row_id, x, u'%s %s %s'%(interns_invoice[counter].name,self.convert_to_vn_date(interns_invoice[counter].date_exam_short),interns_invoice[counter].room_pttt.name), wrap)
                        counter += 1
                    else:
                        sheet.write(row_id, x, u'', wrap)

            else:
                counter = 0
                for x in range(9, 14):
                    if counter < len(interns_invoice) :
                        sheet.write(row_id, x, u'%s %s %s' % (
                        interns_invoice[counter].name, self.convert_to_vn_date(interns_invoice[counter].date_exam_short),
                        interns_invoice[counter].room_pttt.name), wrap)
                        counter += 1
                    else:
                        sheet.write(row_id, x, u'', wrap)
            row_id += 1





TargetHuntReportXlsx('report.intern.hunt.xlsx',
                     'hoanghung.report')


class SalaryChiefReportXlsx(ReportXlsx):
    def convert_to_vn_date(self,date_string):
        if date_string:
            return datetime.strftime(datetime.strptime(date_string, '%Y-%m-%d'),'%d-%m-%Y')
        else:
            return None
    def generate_xlsx_report(self, workbook, data, objects):
        sheet = workbook.add_worksheet(u'Bảng chỉ tiêu khối tuyển dụng')
        title_style = workbook.add_format({'bold': True})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
        wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        header_style = workbook.add_format(
            {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'fg_color': '#96b55e'})
        cate_style = workbook.add_format(
            {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'fg_color': '#7e7e82'})

        row_id = 0
        sheet.write(row_id, 3, u'Bảng chỉ tiêu khối tuyển dụng', title_style)
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 18)

        sheet.write(row_id, 0, u'STT', header_style)
        sheet.write(row_id, 1, u'Họ và tên', header_style)
        sheet.write(row_id, 2, u'GT', header_style)
        sheet.write(row_id, 3, u'Mã số', header_style)
        sheet.write(row_id, 4, u'Năm sinh', header_style)
        sheet.write(row_id, 5, u'Quê quán', header_style)
        sheet.write(row_id, 6, u'CBTD', header_style)
        sheet.write(row_id, 7, u'Phòng TD', header_style)
        sheet.write(row_id, 8, u'Ngày TT', header_style)
        sheet.write(row_id, 9, u'Đơn hàng', header_style)
        sheet.write(row_id, 10, u'Phòng', header_style)
        row_id += 1

        # invoices = self.env['intern.invoice'].search(
        #     [('date_pass', '>=', data['start_date']), ('date_pass', '<=', data['end_date'])])
        # list_interns = Set([])
        # for invoice in invoices:
        #     for intern in invoice.interns_clone:
        #         if intern.pass_exam:
        #             list_interns.add(intern.intern_id.id)

        # interns = self.env['intern.intern'].search([('id','in',list(list_interns))])
        # interns = self.env['intern.internclone'].browse(list(list_interns))

        interns = self.env['intern.internclone'].search([('room_recruitment','!=',False),('date_pass', '>=', data['start_date']),
                                                         ('date_pass', '<=', data['end_date']),('pass_exam','=',True)])

        def get_room_recuitment(x):
            if x.room_recruitment:
                return x.room_recruitment.name
            else:
                return None

        interns = sorted(interns,key=lambda x:get_room_recuitment(x))
        room_recuite = None
        counter = 1
        for intern in interns:
            if intern.room_recruitment.id != room_recuite:
                room_recuite = intern.room_recruitment.id
                counter = 1
                sheet.write(row_id, 0,'',wrap)
                sheet.write(row_id, 1, u'Phòng %s'%intern.room_recruitment.name, cate_style)
                sheet.write(row_id, 2,'', wrap)
                sheet.write(row_id, 3,'', wrap)
                sheet.write(row_id, 4,'', wrap)
                sheet.write(row_id, 5,'', wrap)
                sheet.write(row_id, 6,'', wrap)
                sheet.write(row_id, 7,'', wrap)
                sheet.write(row_id, 8,'', wrap)
                sheet.write(row_id, 9,'', wrap)
                sheet.write(row_id, 10,'', wrap)
                row_id+=1
            sheet.write(row_id, 0, u'%d'%counter, wrap)
            sheet.write(row_id, 1, u'%s' % intern.name, wrap)
            if intern.gender == 'nu':
                sheet.write(row_id, 2, u'Nữ', wrap)
            else:
                sheet.write(row_id, 2, u'Nam', wrap)
            sheet.write(row_id, 3,  u'%s' % intern.custom_id, wrap)
            sheet.write(row_id, 4,  u'%s' % self.convert_to_vn_date(intern.date_of_birth_short), wrap)
            sheet.write(row_id, 5,  u'%s' % intern.province.name, wrap)
            sheet.write(row_id, 6, u'%s' % intern.recruitment_employee.name, wrap)
            sheet.write(row_id, 7, u'%s' % intern.room_recruitment.name, wrap)
            # invoice = self.env['intern.invoice'].browse(intern.invoice_id.id)
            sheet.write(row_id, 8, u'%s'%self.convert_to_vn_date(intern.invoice_id.date_exam_short), wrap)
            sheet.write(row_id, 9, u'%s'%intern.invoice_id.name, wrap)
            sheet.write(row_id, 10, u'%s'%intern.invoice_id.room_pttt.name, wrap)
            row_id+=1
            counter+=1



SalaryChiefReportXlsx('report.salary.chief.xlsx',
                     'hoanghung.report')


