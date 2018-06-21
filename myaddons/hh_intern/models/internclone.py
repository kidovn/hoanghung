# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
import intern_utils
import logging
_logger = logging.getLogger(__name__)

# class Issue(models.Model):
#     _name = 'intern.issue'
#     # name = fields.Char('Tên phát sinh')
#     description = fields.Text('Nội dung')
#     fine_employee = fields.Integer('Phạt CBTD')
#     fine_intern = fields.Integer('Phạt TTS')
#
#     intern_id = fields.Many2one('intern.internclone', ondelete='cascade')


# class IssueAfterExam(models.Model):
#     _name = 'intern.issueafter'
#     # name = fields.Char('Tên phát sinh')
#     description = fields.Text('Nội dung')
#     resolve = fields.Text('Hình thức xử lý')
#     fine_employee = fields.Integer('Phạt CBTD')
#     fine_intern = fields.Integer('Phạt TTS')
#     intern_id = fields.Many2one('intern.internclone', ondelete='cascade')


# class LateDocument(models.Model):
#     _name = 'intern.latedoc'
#     intern_id = fields.Many2one('intern.internclone', ondelete='cascade')
#     #Xin muon hoso
#     number_of_date = fields.Integer("Số ngày muộn", default=1)
#     description = fields.Text('Nội dung')

class Discipline(models.Model):
    _name = 'intern.discipline'
    intern_id = fields.Many2one('intern.intern', ondelete='cascade')
    name = fields.Char('Nội dung')


class InternInvoice(models.Model):
    _name = 'intern.internclone'
    _inherits = {'intern.intern': 'intern_id'}

    _description = 'Thực tập sinh'

    _order = 'id desc'

    intern_id = fields.Many2one('intern.intern', required=True, ondelete='restrict', auto_join=True,
                                  string='Thực tập sinh', help='Intern-related data of the user')

    invoice_id = fields.Many2one("intern.invoice",string='Đơn hàng', ondelete='cascade')


    #du kien tien cu
    promoted = fields.Boolean('Tiến cử')


    #chot thi
    confirm_exam = fields.Boolean('Chốt thi tuyển')

    # escape_exam = fields.Boolean('Rút bỏ chốt thi')

    date_escape_exam = fields.Date('Ngày rút bỏ chốt thi')

    #trung tuyen/du bi

    pass_exam = fields.Boolean('Trúng tuyển')

    date_pass = fields.Datetime(string='Ngày trúng tuyển')

    def confirm_pass(self):
        self.write({
            'date_pass': fields.Datetime.now(),
        })

    preparatory_exam = fields.Boolean('Dự bị')

    cancel_pass = fields.Boolean('Huỷ trúng tuyển')

    reason_cancel_pass = fields.Char('Lý do huỷ TT')


    # #phat sinh trc thi tuyen
    #
    # issues_before = fields.One2many('intern.issue','intern_id',string='Phát sinh trước TT')
    #
    # #phat sinh sau thi tuyen
    #
    # issues_after = fields.One2many('intern.issueafter','intern_id',string='Phát sinh sau TT')

    #Phat sinh
    issues_raise = fields.Boolean('Phát sinh trước thi')
    issues_reason = fields.Text('Lý do phát sinh')
    issues_resolve = fields.Text('Hình thức xử lý')
    fine_employee = fields.Integer('Phạt CBTD')
    fine_intern = fields.Integer('Phạt TTS')

    # Phat sinh

    # issues_resolve_2 = fields.Text('Hình thức xử lý')
    # fine_employee_2 = fields.Integer('Phạt CBTD')
    # fine_intern_2 = fields.Integer('Phạt TTS')





    #xin nhap hoc muon
    admission_late = fields.Integer("Xin nhập học muộn", default=1)
    admission_late_des = fields.Text('Nội dung muộn')

    join_school = fields.Boolean('Đã nhập học')
    date_join_school = fields.Date("Ngày nhập học")

    #hong visa
    visa_failure = fields.Boolean('Hỏng VISA')

    tclt_failure = fields.Boolean('Hỏng TCLT')
    tclt_failure_reason = fields.Char('Lý do hỏng TCLT')

    check_heath_before_departure = fields.Boolean('Sức khoẻ xuất cảnh')
    check_before_fly = fields.Boolean('Kiểm tra trước bay')
    departure = fields.Boolean('Xuất cảnh')
    date_departure = fields.Date('Ngày xuất cảnh')

    comeback = fields.Boolean('Đã về nước')
    date_comeback = fields.Date('Ngày về nước')
    liquidated = fields.Boolean('Đã thanh lý HĐ')
    date_liquidated = fields.Date('Ngày thanh lý hợp đồng')
    reason_comeback = fields.Char('Lý do về nước')



    # current_status = fields.Char("Trạng thái",compute='_compute_status')
    #
    # @api.multi
    # def _compute_status(self):
    #     for obj in self:
    #         if obj.pass_exam:
    #             obj.current_status = u'Trúng tuyển'
    #         elif obj.preparatory_exam:
    #             obj.current_status = u'Dự bị'
    #         elif obj.cancel_pass:
    #             obj.current_status = u'Huỷ sau trúng tuyển'
    #         else:
    #             obj.current_status=""
    exam = fields.Boolean('Đã chốt thi')
    done_exam = fields.Boolean('Đã thi')
    cancel_exam = fields.Boolean('Đã huỷ')

    sequence_exam = fields.Integer('sequence', help="Sequence for the handle.",default=100)
    sequence_pass = fields.Integer('sequence', help="Sequence for the handle.",default=100)

    @api.model
    def create(self, vals):
        if 'issues_raise' in vals:
            if vals['issues_raise']:
                vals['date_escape_exam'] = fields.date.today()
            else:
                vals['date_escape_exam'] = False
        if 'comeback' in vals:
            if vals['comeback']:
                vals['date_comback'] = fields.date.today()
            else:
                vals['date_comback'] = False
        if 'liquidated' in vals:
            if vals['liquidated']:
                vals['date_liquidated'] = fields.date.today()
            else:
                vals['date_liquidated'] = False
        record = super(InternInvoice, self).create(vals)
        return record

    @api.one
    def write(self, vals):
        if 'issues_raise' in vals:
            if vals['issues_raise']:
                vals['date_escape_exam'] = fields.date.today()
            else:
                vals['date_escape_exam'] = False
        if 'departure' in vals:
            if vals['departure']:
                vals['date_departure'] = fields.date.today()
            else:
                vals['date_departure'] = False
        if 'join_school' in vals:
            if vals['join_school']:
                vals['date_join_school'] = fields.date.today()
            else:
                vals['date_join_school'] = False
        super(InternInvoice, self).write(vals)

    #danh sach xin tclt
    phieutraloi_id = fields.Many2one('intern.phieutraloi',string='Phiếu trả lời')

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, record.name))
        return res


    date_duration_previous_in_jp = fields.Char(u'Ngày và thời gian ở Nhật lần trước',default='NO')


    time_at_pc_month = fields.Integer('Tổng thời gian làm việc tại công ty PC2 (tháng)',compute='compute_time_at_pc')
    time_at_pc_year = fields.Integer('Tổng thời gian làm việc tại công ty PC2 (năm)',compute='compute_time_at_pc')

    def compute_time_at_pc(self):
        if self.invoice_id:
            # invoice = self.env['intern.invoice'].browse(self.invoice_id)
            if self.invoice_id.month_create_letter_promotion and self.invoice_id.year_create_letter_promotion \
                and self.time_start_at_pc_from_month and self.time_start_at_pc_from_year:
                try:
                    total_month = (int(self.invoice_id.year_create_letter_promotion) - int(self.time_start_at_pc_from_year))*12 + int(self.invoice_id.month_create_letter_promotion) - int(self.time_start_at_pc_from_month)
                    self.time_at_pc_month = total_month%12
                    self.time_at_pc_year = total_month/12
                except Exception:
                    self.time_at_pc_month = False
                    self.time_at_pc_year = False

            else:
                self.time_at_pc_month = False
                self.time_at_pc_year = False


    current_status_2 = fields.Char("Trạng thái", store=False, compute='_compute_status_2')
    @api.multi
    def _compute_status_2(self):
        for obj in self:
            if 'id' in obj and type(obj['id']) is int:
                self._cr.execute(
                    "SELECT * FROM intern_internclone WHERE intern_internclone.id !=%d AND intern_internclone.intern_id = %d AND COALESCE(intern_internclone.promoted, FALSE) = TRUE AND intern_internclone.create_date > now()::date - interval '3 y'" %
                    (obj['id'],obj['intern_id']))
            else:
                self._cr.execute(
                    "SELECT * FROM intern_internclone WHERE intern_internclone.intern_id = %d AND COALESCE(intern_internclone.promoted, FALSE) = TRUE AND intern_internclone.create_date > now()::date - interval '3 y'" %
                    obj['intern_id'])
            tmpresult = self._cr.dictfetchall()
            count_exam = 0
            for record in tmpresult:
                if record['confirm_exam'] and not record['issues_raise']:
                    count_exam += 1
            obj.current_status_2 = u'Đã TC %d lần, TT %d lần' % (len(tmpresult), count_exam)


    enterprise = fields.Many2one('intern.enterprise',string='Xí nghiệp')