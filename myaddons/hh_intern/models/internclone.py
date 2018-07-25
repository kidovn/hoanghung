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

    _sql_constraints = [('unique_invoice', 'unique(intern_id, invoice_id)',
                         'Lỗi trùng TTS trong danh sách dự kiến tiến cử. F5 nếu bạn ko thấy.')]

    intern_id = fields.Many2one('intern.intern', required=True, ondelete='restrict', auto_join=True,
                                  string='Thực tập sinh', help='Intern-related data of the user',index=True)

    invoice_id = fields.Many2one("intern.invoice",string='Đơn hàng', ondelete='cascade',index=True)


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
    phieutraloi_id = fields.Many2one('intern.phieutraloi',string='Phiếu trả lời',index=True)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, record.name))
        return res


    date_duration_previous_in_jp = fields.Char(u'Ngày và thời gian ở Nhật lần trước',default='NO')


    time_at_pc_month = fields.Integer('Tổng thời gian làm việc tại công ty PC2 (tháng)',compute='compute_time_at_pc')
    time_at_pc_year = fields.Integer('Tổng thời gian làm việc tại công ty PC2 (năm)',compute='compute_time_at_pc')

    # day_create_letter_promotion = fields.Char("Ngày", size=2, compute='compute_time_create_letter')
    # month_create_letter_promotion = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
    #                                                   ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
    #                                                   ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ],
    #                                                  "Tháng", compute='compute_time_create_letter')
    # year_create_letter_promotion = fields.Char("Năm", compute='compute_time_create_letter')
    #
    #
    # @api.multi
    # def compute_time_create_letter(self):
    #     for rec in self:
    #         if rec.invoice_id:
    #             rec.day_create_letter_promotion = rec.invoice_id.day_create_letter_promotion
    #             rec.month_create_letter_promotion = rec.invoice_id.month_create_letter_promotion
    #             rec.year_create_letter_promotion = rec.invoice_id.year_create_letter_promotion


    @api.multi
    @api.onchange('time_start_at_pc_from_month', 'time_start_at_pc_from_year')
    def compute_time_at_pc(self):
        for rec in self:
            if rec.invoice_id:
                if rec.invoice_id.month_create_letter_promotion and rec.invoice_id.year_create_letter_promotion \
                    and rec.time_start_at_pc_from_month and rec.time_start_at_pc_from_year:
                    try:
                        total_month = (int(rec.invoice_id.year_create_letter_promotion) - int(rec.time_start_at_pc_from_year))*12 + int(rec.invoice_id.month_create_letter_promotion) - int(rec.time_start_at_pc_from_month)
                        rec.time_at_pc_month = total_month%12
                        rec.time_at_pc_year = total_month/12
                    except Exception:
                        rec.time_at_pc_month = False
                        rec.time_at_pc_year = False

                else:
                    rec.time_at_pc_month = False
                    rec.time_at_pc_year = False

    # @api.multi
    # @api.onchange('time_start_at_pc_from_month','time_start_at_pc_from_year','month_create_letter_promotion','year_create_letter_promotion')
    # @api.depends('time_start_at_pc_from_month','time_start_at_pc_from_year','month_create_letter_promotion','year_create_letter_promotion')
    # def compute_time_at_pc(self):
    #     for rec in self:
    #         if rec.month_create_letter_promotion and rec.year_create_letter_promotion \
    #             and rec.time_start_at_pc_from_month and rec.time_start_at_pc_from_year:
    #             try:
    #                 total_month = (int(rec.year_create_letter_promotion) - int(rec.time_start_at_pc_from_year))*12 + int(rec.month_create_letter_promotion) - int(rec.time_start_at_pc_from_month)
    #                 rec.time_at_pc_month = total_month%12
    #                 rec.time_at_pc_year = total_month/12
    #             except Exception:
    #                 rec.time_at_pc_month = False
    #                 rec.time_at_pc_year = False
    #
    #         else:
    #             rec.time_at_pc_month = False
    #             rec.time_at_pc_year = False


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
    dispatchcom2 = fields.Many2one('dispatchcom2', string=u'Công ty phái cử thứ 2')

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain is not None:
            _logger.info("DOMAIN %s" % str(domain))
            for x in domain:
                if x[0] == 'name':
                    x[0] = 'name_without_signal'
                    x[2] = intern_utils.no_accent_vietnamese(x[2])
                if x[0] == 'identity' and len(domain) == 1:
                    term = x[2]
                    domain = ['|', ['identity', 'ilike', term], ['identity_2', 'ilike', term]]
                    break
            _logger.info("DOMAIN %s" % str(domain))
        return super(InternInvoice, self).search_read(domain, fields, offset, limit, order)

    @api.multi
    @api.depends('name')
    def _calculate_name(self):
        for rec in self:
            rec.notice_name = ""
            if rec.name:
                tmpName = intern_utils.fix_accent_2(intern_utils.no_accent_vietnamese2(rec.name))
                words = tmpName.split()
                for i, word in enumerate(words):
                    jps = self.env['intern.translator'].search([('vi_word', '=', word.upper())], limit=1)
                    if not jps:
                        rec.notice_name = "Một số từ trong tên TTS không có trong từ điển, vui lòng nhập tên tiếng Nhật của TTS"
                        return

    @api.onchange('name')  # if these fields are changed, call method
    def name_change(self):
        if self.name:
            self.name_without_signal = intern_utils.no_accent_vietnamese(self.name)
            tmp = self.convertToJP(intern_utils.fix_accent_2(intern_utils.no_accent_vietnamese2(self.name)))
            if tmp is not None:
                self.name_in_japan = tmp

    def convertToJP(self, name):
        words = name.split()
        final = ""
        for i, word in enumerate(words):
            jps = self.env['intern.translator'].search([('vi_word', '=', word.upper())], limit=1)
            if jps:
                if i > 0:
                    final = final + u"・"
                final = final + jps[0].jp_word
            else:
                return ""
        return final

    @api.multi
    @api.depends('certification')
    @api.onchange('certification')  # if these fields are changed, call method
    def certification_change(self):
        for rec in self:
            if rec.certification:
                if rec.certification.id == 1:
                    rec.specialized = u'無し'
                    rec.show_specialized = False

                elif rec.certification.id == 2:
                    rec.specialized = u'無し'
                    rec.show_specialized = False
                else:
                    rec.specialized = ""
                    rec.show_specialized = True
            else:
                rec.show_specialized = False

