# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.addons.hh_intern.models import intern_utils
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
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
        # list_code_prepare = []
        has_prepare = False
        interns = sorted(invoice.interns_clone, key=lambda l: l[0].sequence_exam)
        for intern in interns:
            if intern.pass_exam:
                list_code.append(intern.id)
            if intern.preparatory_exam:
                # list_code_prepare.append(intern.id)
                has_prepare = True

        today = intern_utils.date_time_in_vn_lower(datetime.today().day,datetime.today().month,datetime.today().year)
        docargs = {
            'record': invoice,
            'interns':interns,
            'codes':list_code,
            'has_prepare':has_prepare,
            'today':today
        }
        return self.env['report'].render('hh_intern_pass_report.report_intern_pass_view', values=docargs)


class InternPassReportAnnounceXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, invoices):
        for obj in invoices:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            title_style = workbook.add_format({'bold': True})
            bold = workbook.add_format({'bold': True,'align': 'center','valign': 'vcenter','border':1})
            center = workbook.add_format({'align': 'center','valign':   'vcenter','border':1})
            wrap = workbook.add_format({'text_wrap': True,'align': 'center','valign': 'vcenter','border':1})
            header_style = workbook.add_format({'bold': True,'text_wrap': True,'align': 'center','valign': 'vcenter','border':1,'fg_color': '#96b55e'})

            bold_no_border = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
            no_border = workbook.add_format({'valign': 'vcenter'})
            wrap_no_border = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter'})

            row_id = 0
            #TITLE
            sheet.write(row_id, 0, u'DANH SÁCH TRÚNG TUYỂN CHÍNH THỨC', title_style)

            row_id+=2
            #TABLE HEADER
            sheet.write(row_id,0,u'STT',header_style)
            sheet.write(row_id,1,u'Mã số',header_style)
            sheet.write(row_id,2,u'Họ và tên',header_style)
            sheet.write(row_id,3,u'Giới tính',header_style)
            sheet.write(row_id,4,u'Năm sinh',header_style)
            sheet.write(row_id,5,u'Quê quán',header_style)
            sheet.write(row_id,6,u'CBTD',header_style)
            sheet.write(row_id,7,u'Phòng TD',header_style)
            sheet.write(row_id,8,u'Xí nghiệp',header_style)
            sheet.write(row_id,9,u'Nghiệp đoàn',header_style)
            sheet.write(row_id,10,u'Địa chỉ làm việc',header_style)
            sheet.write(row_id,11,u'Ngành nghề',header_style)
            sheet.write(row_id,12,u'Hạn HĐ',header_style)
            sheet.write(row_id,13,u'Ngày trúng tuyển',header_style)
            sheet.write(row_id,14,u'Ngày nhập học trúng tuyển',header_style)
            sheet.write(row_id,15,u'Ngày dự kiến xuất cảnh',header_style)
            sheet.write(row_id,16,u'Pháp nhân',header_style)

            sheet.set_row(row_id, 40)

            #TABLE BODY
            row_id += 1
            preparation = False
            issued = False
            interns = sorted(obj.interns_clone, key=lambda x: x.sequence_exam)
            iterator = 1
            for intern in interns:
                if intern.pass_exam and not intern.cancel_pass:
                    sheet.write(row_id,0,iterator,center)
                    sheet.write(row_id,1,intern.custom_id,center)
                    sheet.write(row_id, 2, u'%s'%intern.name,center)
                    if intern.gender=='nu':
                        sheet.write(row_id, 3, u'Nữ',center)
                    else:
                        sheet.write(row_id, 3, u'Nam', center)
                    sheet.write(row_id, 4, u'%s'%datetime.strftime(datetime.strptime(intern.date_of_birth_short,'%Y-%m-%d'),'%d-%m-%Y'),center)
                    sheet.write(row_id, 5, u'%s'%intern.province.name,center)
                    sheet.write(row_id, 6, u'%s'%intern.recruitment_employee.name,center)
                    sheet.write(row_id, 7, u'%s'%intern.room_recruitment.name,center)
                    sheet.write(row_id, 8, u'%s\n%s'%(intern.enterprise.name_jp,intern.enterprise.name_romaji),wrap)
                    sheet.write(row_id, 9, u'%s'%obj.guild.name_acronym,center)
                    sheet.write(row_id, 10, u'%s'%obj.place_to_work,center)
                    sheet.write(row_id, 11, u'%s\n%s'%(obj.job_vi,obj.job_jp),wrap)
                    sheet.write(row_id, 12, u'%s năm'%obj.year_expire,center)
                    sheet.write(row_id, 13, u'%s'%datetime.strftime(datetime.strptime(obj.date_pass,'%Y-%m-%d'),'%d-%m-%Y'),center)
                    sheet.write(row_id, 14,u'%s'%datetime.strftime(datetime.strptime(obj.date_join_school,'%Y-%m-%d'),'%d-%m-%Y'),center)
                    sheet.write(row_id, 15, u'%s'%datetime.strftime(datetime.strptime(obj.date_departure,'%Y-%m-%d'),'%d-%m-%Y'),center)
                    sheet.write(row_id, 16, u'%s'%obj.dispatchcom1.name_short,center)
                    iterator+=1
                    row_id+=1
                elif intern.preparatory_exam and not intern.cancel_pass:
                    preparation = True
                elif intern.cancel_pass:
                    issued = True

            if issued:
                row_id += 2
                sheet.write(row_id, 0, u'DANH SÁCH PHÁT SINH KHÔNG ĐI', title_style)
                row_id += 2
                # TABLE HEADER
                sheet.write(row_id, 0, u'STT', header_style)
                sheet.write(row_id, 1, u'Mã số', header_style)
                sheet.write(row_id, 2, u'Họ và tên', header_style)
                sheet.write(row_id, 3, u'Giới tính', header_style)
                sheet.write(row_id, 4, u'Năm sinh', header_style)
                sheet.write(row_id, 5, u'Quê quán', header_style)
                sheet.write(row_id, 6, u'CBTD', header_style)
                sheet.write(row_id, 7, u'Phòng TD', header_style)
                sheet.write(row_id, 8, u'Xí nghiệp', header_style)
                sheet.write(row_id, 9, u'Nghiệp đoàn', header_style)
                sheet.write(row_id, 10, u'Địa chỉ làm việc', header_style)
                sheet.write(row_id, 11, u'Ngành nghề', header_style)
                sheet.write(row_id, 12, u'Hạn HĐ', header_style)
                sheet.write(row_id, 13, u'Ngày trúng tuyển', header_style)
                sheet.write(row_id, 14, u'Ngày nhập học trúng tuyển', header_style)
                sheet.write(row_id, 15, u'Ngày dự kiến xuất cảnh', header_style)
                sheet.write(row_id, 16, u'Pháp nhân', header_style)

                sheet.set_row(row_id, 40)

                iterator = 1
                row_id += 1
                for intern in interns:
                    if intern.cancel_pass:
                        sheet.write(row_id, 0, iterator, center)
                        sheet.write(row_id, 1, intern.custom_id, center)
                        sheet.write(row_id, 2, u'%s' % intern.name, center)
                        if intern.gender == 'nu':
                            sheet.write(row_id, 3, u'Nữ', center)
                        else:
                            sheet.write(row_id, 3, u'Nam', center)
                        sheet.write(row_id, 4,
                                    u'%s' % datetime.strftime(datetime.strptime(intern.date_of_birth_short, '%Y-%m-%d'),
                                                              '%d-%m-%Y'), center)
                        sheet.write(row_id, 5, u'%s' % intern.province.name, center)
                        sheet.write(row_id, 6, '', center)
                        sheet.write(row_id, 7, '', center)
                        sheet.write(row_id, 8, '', center)
                        sheet.write(row_id, 9, '', center)
                        sheet.write(row_id, 10, '', center)
                        sheet.write(row_id, 11, '', center)
                        sheet.write(row_id, 12, '', center)
                        sheet.write(row_id, 13, '', center)
                        sheet.write(row_id, 14, '', center)
                        sheet.write(row_id, 15, '', center)
                        sheet.write(row_id, 16, '', center)
                        sheet.set_row(row_id, 40)
                        iterator += 1
                        row_id += 1

            if preparation:
                row_id += 2
                sheet.write(row_id, 0, u'DANH SÁCH DỰ BỊ', title_style)
                row_id += 2
                # TABLE HEADER
                sheet.write(row_id, 0, u'STT', header_style)
                sheet.write(row_id, 1, u'Mã số', header_style)
                sheet.write(row_id, 2, u'Họ và tên', header_style)
                sheet.write(row_id, 3, u'Giới tính', header_style)
                sheet.write(row_id, 4, u'Năm sinh', header_style)
                sheet.write(row_id, 5, u'Quê quán', header_style)
                sheet.write(row_id, 6, u'CBTD', header_style)
                sheet.write(row_id, 7, u'Phòng TD', header_style)
                sheet.write(row_id, 8, u'Xí nghiệp', header_style)
                sheet.write(row_id, 9, u'Nghiệp đoàn', header_style)
                sheet.write(row_id, 10, u'Địa chỉ làm việc', header_style)
                sheet.write(row_id, 11, u'Ngành nghề', header_style)
                sheet.write(row_id, 12, u'Hạn HĐ', header_style)
                sheet.write(row_id, 13, u'Ngày trúng tuyển', header_style)
                sheet.write(row_id, 14, u'Ngày nhập học trúng tuyển', header_style)
                sheet.write(row_id, 15, u'Ngày dự kiến xuất cảnh', header_style)
                sheet.write(row_id, 16, u'Pháp nhân', header_style)

                sheet.set_row(row_id, 40)

                iterator = 1
                row_id += 1
                for intern in interns:
                    if intern.preparatory_exam and not intern.cancel_pass:
                        sheet.write(row_id, 0, iterator, center)
                        sheet.write(row_id, 1, intern.custom_id, center)
                        sheet.write(row_id, 2, u'%s' % intern.name, center)
                        if intern.gender == 'nu':
                            sheet.write(row_id, 3, u'Nữ', center)
                        else:
                            sheet.write(row_id, 3, u'Nam', center)
                        sheet.write(row_id, 4,
                                    u'%s' % datetime.strftime(datetime.strptime(intern.date_of_birth_short, '%Y-%m-%d'),
                                                              '%d-%m-%Y'), center)
                        sheet.write(row_id, 5, u'%s' % intern.province.name, center)
                        sheet.write(row_id, 6, '', center)
                        sheet.write(row_id, 7, '', center)
                        sheet.write(row_id, 8, '', center)
                        sheet.write(row_id, 9, '', center)
                        sheet.write(row_id, 10, '', center)
                        sheet.write(row_id, 11, '', center)
                        sheet.write(row_id, 12, '', center)
                        sheet.write(row_id, 13, '', center)
                        sheet.write(row_id, 14, '', center)
                        sheet.write(row_id, 15, '', center)
                        sheet.write(row_id, 16, '', center)
                        sheet.set_row(row_id, 40)
                        iterator += 1
                        row_id += 1

            row_id+=1
            sheet.write(row_id,5,u'Phê duyệt',bold_no_border)
            sheet.write(row_id,10,u'Đại diện %s'%obj.room_pttt.name,bold_no_border)
            row_id+=1
            sheet.write(row_id,1,u'Nơi nhận:',bold_no_border)
            row_id += 1
            sheet.write(row_id,1,u"- BĐH (báo cáo)",no_border)
            row_id += 1
            sheet.write(row_id,1,u"- Trưởng phòng TD",no_border)
            row_id += 1
            sheet.write(row_id, 1, u"- Hiệu trưởng TTĐT", no_border)
            row_id += 1
            sheet.write(row_id, 1, u"- Kế toán trưởng", no_border)
            sheet.write(row_id, 5, u"Nguyễn Minh Huyên", bold_no_border)
            sheet.write(row_id, 10, u'%s'%obj.room_pttt.name,bold_no_border)



            sheet.set_column(0, 0, 5)
            sheet.set_column(1, 1, 8)
            sheet.set_column(2, 2, 18)
            sheet.set_column(3, 3, 8)
            sheet.set_column(4, 4, 12)
            sheet.set_column(5, 5, 12)
            sheet.set_column(6, 6, 18)
            sheet.set_column(7, 7, 25)
            sheet.set_column(8, 8, 20)
            sheet.set_column(9, 9, 18)
            sheet.set_column(10, 10, 10)
            sheet.set_column(11, 11, 20)
            sheet.set_column(12, 12, 7)
            sheet.set_column(13, 13, 12)
            sheet.set_column(14, 14, 12)
            sheet.set_column(15, 15, 12)
            sheet.set_column(16, 16, 12)


InternPassReportAnnounceXlsx('report.intern.invoice.pass.xlsx',
            'intern.invoice')



class InternExamReportXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, invoices):
        for obj in invoices:
            report_name = obj.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            title_style = workbook.add_format({'bold': True})
            bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
            center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
            wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
            header_style = workbook.add_format(
                {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
                 'fg_color': '#96b55e'})


            interns = sorted(obj.interns_clone, key=lambda x: x.sequence_exam)
            iterator = 1
            has_women = False
            has_man = False
            for intern in interns:
                if intern.confirm_exam:
                    if intern.gender == 'nu':
                        has_women = True
                    else:
                        has_man = True

            row_id = 0
            if has_man:
                row_id+=1
                sheet.write(row_id, 0, u'STT', header_style)
                sheet.write(row_id, 1, u'Họ và tên', header_style)
                sheet.write(row_id, 2, u'Giới tính', header_style)
                sheet.write(row_id, 3, u'Năm sinh', header_style)
                sheet.write(row_id, 4, u'Quê quán', header_style)
                row_id += 1
                for intern in interns:
                    if intern.confirm_exam and not intern.gender == 'nu':
                        sheet.write(row_id, 0, iterator, center)
                        sheet.write(row_id, 1, u'%s' % intern.name, center)

                        sheet.write(row_id, 2, u'Nam', center)
                        sheet.write(row_id, 3,
                                    u'%s' % datetime.strftime(datetime.strptime(intern.date_of_birth_short, '%Y-%m-%d'),
                                                              '%d-%m-%Y'), center)
                        sheet.write(row_id, 4, u'%s' % intern.province.name, center)

                        iterator+=1
                        row_id += 1

            if has_women:
                row_id += 1
                sheet.write(row_id, 0, u'STT', header_style)
                sheet.write(row_id, 1, u'Họ và tên', header_style)
                sheet.write(row_id, 2, u'Giới tính', header_style)
                sheet.write(row_id, 3, u'Năm sinh', header_style)
                sheet.write(row_id, 4, u'Quê quán', header_style)
                row_id += 1
                for intern in interns:
                    if intern.confirm_exam and intern.gender == 'nu':
                        sheet.write(row_id, 0, iterator, center)
                        sheet.write(row_id, 1, u'%s' % intern.name, center)

                        sheet.write(row_id, 2, u'Nữ', center)
                        sheet.write(row_id, 3,
                                    u'%s' % datetime.strftime(datetime.strptime(intern.date_of_birth_short, '%Y-%m-%d'),
                                                              '%d-%m-%Y'), center)
                        sheet.write(row_id, 4, u'%s' % intern.province.name, center)

                        iterator += 1
                        row_id += 1

            sheet.set_column(0, 0, 5)
            sheet.set_column(1, 1, 18)
            sheet.set_column(3, 3, 12)
            sheet.set_column(4, 4, 15)




InternExamReportXlsx('report.intern.invoice.exam.xlsx',
                                     'intern.invoice')


class InternPromotedReportXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, invoices):
        for obj in invoices:
            report_name = u'Danh sách tiến cử đơn hàng %s'%(obj.name)
            if obj.date_exam_short:
                report_name+=u' ngày %s'%datetime.strftime(datetime.strptime(obj.date_exam_short, '%Y-%m-%d'),'%d/%m/%Y')
            sheet = workbook.add_worksheet(report_name[:31])
            title_style = workbook.add_format({'bold': True})
            bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
            center = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
            wrap = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
            header_style = workbook.add_format(
                {'bold': True, 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,
                 'fg_color': '#96b55e'})

            row_id = 0
            sheet.write(row_id, 3, report_name, title_style)
            row_id+=2
            sheet.write(row_id, 0, u'STT', header_style)
            sheet.write(row_id, 1, u'Họ và tên', header_style)
            sheet.write(row_id, 2, u'Giới tính', header_style)
            sheet.write(row_id, 3, u'Mã số', header_style)
            sheet.write(row_id, 4, u'Ngày NH', header_style)
            sheet.write(row_id, 5, u'Năm sinh', header_style)
            sheet.write(row_id, 6, u'Tuổi', header_style)
            sheet.write(row_id, 7, u'Cao', header_style)
            sheet.write(row_id, 8, u'Nặng', header_style)
            sheet.write(row_id, 9, u'Nhóm máu', header_style)
            sheet.write(row_id, 10, u'Thị lực', header_style)
            sheet.write(row_id, 11, u'Tình trạng HN', header_style)
            sheet.write(row_id, 12, u'Trình độ học vấn', header_style)
            sheet.write(row_id, 13, u'TB', header_style)
            sheet.write(row_id, 14, u'Cộng dồn', header_style)
            sheet.write(row_id, 15, u'Quê quán', header_style)
            sheet.write(row_id, 16, u'CBTD', header_style)
            row_id += 1
            counter=1
            for intern in obj.interns_clone:
                if intern.promoted:
                    sheet.write(row_id, 0, counter, center)
                    sheet.write(row_id, 1, u'%s' % intern.name, center)
                    if intern.gender == 'nu':
                        sheet.write(row_id, 2, u'Nữ', center)
                    else:
                        sheet.write(row_id, 2, u'Nam', center)
                    sheet.write(row_id, 3,intern.custom_id, center)
                    if intern.date_enter_source:
                        sheet.write(row_id, 4, datetime.strftime(datetime.strptime(intern.date_enter_source, '%Y-%m-%d'),'%d/%m/%Y'), center)
                    if intern.date_of_birth_short:
                        sheet.write(row_id, 5, datetime.strftime(datetime.strptime(intern.date_of_birth_short, '%Y-%m-%d'),'%d/%m/%Y'), center)
                        sheet.write(row_id, 6, datetime.now().year - int(datetime.strptime(intern.date_of_birth_short, '%Y-%m-%d').year), center)
                    sheet.write(row_id, 7, intern.height, center)
                    sheet.write(row_id, 8, intern.weight, center)
                    sheet.write(row_id, 9, intern.blood_group, center)
                    sheet.write(row_id, 10, u'%d/%d'%(intern.vision_left,intern.vision_right), center)
                    if intern.marital_status:
                        if intern.marital_status.name_in_vn == u'Độc thân':
                            sheet.write(row_id, 11, u'C', center)
                        elif intern.marital_status.name_in_vn == u'Kết hôn':
                            sheet.write(row_id, 11, u'R', center)
                        else:
                            sheet.write(row_id, 11, u'R(ly hôn)', center)
                    if intern.certification:
                        if u'cao đẳng' in intern.certification.name_in_vn :
                            sheet.write(row_id, 12, u'CĐ', center)
                        elif u'THCS' in intern.certification.name_in_vn :
                            sheet.write(row_id, 12, u'THCS', center)
                        elif u'THPT' in intern.certification.name_in_vn :
                            sheet.write(row_id, 12, u'THPT', center)
                        elif u'trung cấp' in intern.certification.name_in_vn :
                            sheet.write(row_id, 12, u'TC', center)
                        else:
                            sheet.write(row_id, 12, u'ĐH', center)

                    sheet.write(row_id, 13, u'%s%%'%intern.iq_percentage, center)
                    sheet.write(row_id, 14, intern.check_kureperin, center)
                    if intern.province:
                        sheet.write(row_id, 15, u'%s'%intern.province.name, center)
                    if intern.recruitment_employee:
                        sheet.write(row_id, 16, u'%s'%intern.recruitment_employee.name, center)
                    counter += 1
                    row_id += 1
            sheet.set_column(0, 0, 5)
            sheet.set_column(1, 1, 18)
            sheet.set_column(2, 2, 5)
            sheet.set_column(4, 4, 12)
            sheet.set_column(5, 5, 15)
            sheet.set_column(6, 6, 5)
            sheet.set_column(7, 7, 5)
            sheet.set_column(8, 8, 6)
            sheet.set_column(9, 9, 6)
            sheet.set_column(10, 10, 7)
            sheet.set_column(11, 11, 7)
            sheet.set_column(12, 12, 6)
            sheet.set_column(13, 13, 7)
            sheet.set_column(14, 14, 5)
            sheet.set_column(15, 15, 12)
            sheet.set_column(16, 16, 18)

InternPromotedReportXlsx('report.intern.invoice.promoted.xlsx',
                                     'intern.invoice')