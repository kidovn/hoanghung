# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
import intern_utils
import province
_logger = logging.getLogger(__name__)


class Promotion(models.Model):
    _name = 'intern.promotion'
    _description = u'Tiến cử'
    intern = fields.Many2one("intern.internks",required=True,ondelete='cascade')
    day = fields.Char("Ngày", size=2)
    month = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    date = fields.Char("Ngày", store=False, compute='_date')
    @api.one
    @api.depends('day', 'month', 'year')
    def _date(self):
        if self.day and self.month and self.year:
            self.date = u"%s Tháng %s Năm %s" % (self.day, self.month, self.year)
        else:
            self.date = ""

    invoice = fields.Char("Đơn hàng", required=True)

    @api.model
    def _get_current_year(self):
        return str(datetime.now().year)



class InternEducationVi(models.Model):
    _name = 'intern.educationvi'
    _inherit = 'intern.education'

    @api.onchange('school_type')  # if these fields are changed, call method
    def school_type_change(self):
        _logger.info("")



class InternEmploymentVi(models.Model):
    _name = 'intern.employmentvi'
    _inherit = 'intern.employment'
    # info = fields.Many2one("intern.intern",required=True,ondelete='cascade')
    # month_start = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
    #                                     ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
    #                                     ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")
    #
    # year_start = fields.Char("Năm bắt đầu", size=4,required=True)
    #
    # month_end = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
    #                                     ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
    #                                     ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")
    # year_end = fields.Char("Năm kết thúc", size=4,required=True)
    #
    # company = fields.Char("Tên công ty",required=True)
    # description = fields.Char("Lý lịch làm việc")



class InternFamilyVi(models.Model):
    _name = 'intern.familyvi'
    _inherit = 'intern.family'

def percentage(part, whole):
    return round(100.0 * float(part)/float(whole),0)

class InternKS(models.Model):
    _name = 'intern.internks'
    _description = 'Thực tập sinh'

    # serial = fields.Char("Mã số")
    # long_term = fields.Boolean("Đăng ký dài hạn")
    enter_source = fields.Selection([('1','Ngắn hạn'),('2','Dài hạn'),('3','Ban chỉ đạo'),('4','Rút bỏ nguồn')],'Đăng ký nguồn')

    enter_source_tmp = fields.Char('Old enter source')

    date_enter_source = fields.Date('Ngày vào nguồn')

    date_escape_source = fields.Date('Ngày rời nguồn')

    identity = fields.Char("CMND")
    identity_2 = fields.Char("Thẻ căn cước")



    day_identity = fields.Char("Ngày", size=2)
    month_identity = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_identity = fields.Char("Năm", size=4)

    date_identity = fields.Char("Ngày cấp", store=False, compute='_date_of_identity')

    @api.one
    @api.depends('day_identity', 'month_identity', 'year_identity')
    def _date_of_identity(self):
        if self.day_identity and self.month_identity and self.year_identity:
            self.date_identity = u"%s Tháng %s Năm %s" % (self.day_identity, self.month_identity, self.year_identity)
        else:
            self.date_identity = ""

    place_cmnd = fields.Many2one("province",string="Nơi cấp")

    name = fields.Char("Họ tên", required=True)

    gender = fields.Selection([('nam', 'Nam'), ('nu', 'Nữ')],string='Giới tính')
    day = fields.Char("Ngày", size=2)
    month = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year = fields.Char("Năm", size=4)

    date_of_birth = fields.Char("Ngày sinh", store=False, compute='_date_of_birth')

    name_without_signal = fields.Char("Tên tiếng Việt ko dấu")
    name_in_japan = fields.Char("Họ tên tiếng Nhật")

    address = fields.Char('Địa chỉ liên hệ')
    province = fields.Many2one("province", string="Tỉnh/TP")
    avatar = fields.Binary("Ảnh")

    marital_status = fields.Many2one('marital', string="Tình trạng hôn nhân")
    height = fields.Integer("Chiều cao (cm)")
    weight = fields.Integer("Cân nặng (kg)")
    vision_left = fields.Integer("Mắt trái")
    vision_right = fields.Integer("Mắt phải")

    blood_group = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O')], 'Nhóm máu')

    note_health = fields.Char("Ghi chú sức khỏe")


    check_kureperin = fields.Selection([('A+', 'A+'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
                                       "Kiểm tra kureperin")

    certification = fields.Many2one('intern.certification', "Bằng cấp")

    @api.one
    @api.depends('day', 'month', 'year')
    def _date_of_birth(self):
        if self.day and self.month and self.year:
            self.date_of_birth = u"%s Tháng %s Năm %s" % (self.day, self.month, self.year)
        else:
            self.date_of_birth = ""


    @api.constrains('day')
    def _check_day(self):
        if not self.day:
            raise ValidationError("Sai ngày sinh")
        else:
            tmpDay = int(self.day)
            if tmpDay <= 0 or tmpDay > 31:
                raise ValidationError("Sai ngày sinh")

    @api.constrains('month')
    def _check_month(self):
        if not self.month:
            raise ValidationError("Sai ngày sinh")

    @api.constrains('year')
    def _check_year(self):
        if not self.year:
            raise ValidationError("Sai ngày sinh")
        else:
            if int(self.year) <= 1900:
                raise ValidationError("Sai ngày sinh")

    phone_number = fields.Char("Số điện thoại")
    phone_number_relative = fields.Char("Số điện thoại người thân")
    relative_note = fields.Many2one('relation',string='Quan hệ với TTS')

    phone_number_relative_2 = fields.Char("Số điện thoại người thân")
    relative_note_2 = fields.Many2one('relation', string='Quan hệ với TTS')

    #ngay nop ho so
    day_sent_doc = fields.Char("Ngày", size=2)
    month_sent_doc = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")


    year_sent_doc = fields.Char("Năm", size=4,default=lambda self: self._get_current_year())

    date_sent_doc = fields.Char("Ngày gửi hồ sơ", store=False, compute='_date_send_doc')
    @api.one
    @api.depends('day_sent_doc', 'month_sent_doc', 'year_sent_doc')
    def _date_send_doc(self):
        if self.day_sent_doc and self.month_sent_doc and self.year_sent_doc:
            self.date_sent_doc = u"%s Tháng %s Năm %s" % (self.day_sent_doc, self.month_sent_doc, self.year_sent_doc)
        else:
            self.date_sent_doc = ""

    @api.model
    def _get_current_year(self):
        return str(datetime.now().year)



    # date_of_birth = fields.Char("Ngày sinh", store=False, compute='_date_of_birth')
    #
    # @api.one
    # @api.depends('day', 'month', 'year')
    # def _date_of_birth(self):
    #     self.date_of_birth = "%s/%s/%s" % (self.day, self.month, self.year)



    #test
    logic_correct = fields.Integer()
    logic_done = fields.Integer()
    logic_percentage = fields.Char(string='Điểm logic',store=False,compute='_cal_logic_percentage')

    @api.one
    def _cal_logic_percentage(self):
        if self.logic_done is not 0:
            self.logic_percentage = "%d" % (percentage(self.logic_correct, self.logic_done))


    add_correct = fields.Integer()
    add_done = fields.Integer()
    add_percentage = fields.Char(string='Điểm cộng(IQ)',store=False,compute='_cal_add_percentage')

    @api.one
    def _cal_add_percentage(self):
        if self.add_done is not 0:
            self.add_percentage = "%d"%(percentage(self.add_correct,self.add_done))

    calculation_correct = fields.Integer()
    calculation_done = fields.Integer()
    calculation_percentage = fields.Char(string='Điểm cộng trừ nhân chia(IQ)',store=False,compute='_cal_calculation_percentage')

    @api.one
    def _cal_calculation_percentage(self):
        if self.calculation_done is not 0:
            self.calculation_percentage ="%d"%(percentage(self.calculation_correct,self.calculation_done))

    notice_correct = fields.Integer()
    notice_done = fields.Integer()
    notice_percentage = fields.Char(string='Điểm chú ý(IQ)',store=False,compute='_cal_notice_percentage')

    @api.one
    def _cal_notice_percentage(self):
        if self.notice_done is not 0:
            self.notice_percentage ="%d"%(percentage(self.notice_correct,self.notice_done))

    total_correct = fields.Integer(store=False,compute='_cal_total_corect')
    total_question = fields.Integer("Tổng số câu", default=133)
    iq_percentage = fields.Char("Trung bình cộng"
                                # ,compute='_cal_total_percentage'
                                )

    @api.multi
    def _cal_total_corect(self):
        for rec in self:
            rec.total_correct = rec.logic_correct + rec.add_correct + rec.calculation_correct + rec.notice_correct
        # _logger.info("Total_percentage " + str(self.total_correct) + " " + str(self.total_question))
            if rec.total_question is not 0:
                rec.iq_percentage = "%d" % (percentage(rec.total_correct, rec.total_question))
            # _logger.info("PEE" + self.total_percentage)

    @api.multi
    @api.onchange('total_question','total_correct')
    def _cal_total_percentage(self):
        for rec in self:
            if rec.total_question is not 0:
                rec.iq_percentage = "%d" % (percentage(rec.total_correct, rec.total_question))





    average = fields.Float(u"Trung bình cộng", store=False)
    # incremental = fields.Integer(u"Cộng dồn")

    room_recruitment = fields.Many2one("department",string=u"Phòng tuyển dụng")
    recruitment_employee = fields.Many2one('hh.employee',string=u"Cán bộ tuyển dụng")


    user_access = fields.Many2many("res.users",default=lambda self: self.env.user, string="User có quyền xem")

    # @api.model
    # def name_search(self, name, args=None, operator='ilike', limit=100):
    #     args = args or []
    #     recs = self.browse()
    #     _logger.info("NAME--------------- %s %s" % (name, str(args)))
    #     if name:
    #         recs = self.search([('name_without_signal', 'ilike', intern_utils.no_accent_vietnamese(name))] + args,
    #                            limit=limit)
    #         if not recs:
    #             recs = self.search([('name_in_japan', operator, name)] + args, limit=limit)
    #     return recs.name_get()


    intern_status = fields.Selection([('1','Trúng tuyển'),('2','Dự bị'),('3','Nhập học'),('4','Kỷ luật'),
                                      ('5','Huỷ TT'),('6','Huỷ XC/TCLT'),('7','Xuất cảnh')])


class InternDN(models.Model):
    _name = 'intern.interndn'
    # _inherits = {'intern.internks': 'intern_id'}

    _description = 'Thực tập sinh'

    # intern_id = fields.Many2one('intern.internks', required=True, ondelete='restrict', auto_join=True,
    #                              string='Related Intern', help='Intern-related data of the user')


    blindness = fields.Boolean("Bệnh mù màu")
    smoking = fields.Boolean("Có hút thuốc")
    preferred_hand = fields.Selection((('0', 'Tay phải'), ('1', 'Tay trái'),('2','Cả 2 tay')), string="Tay thuận", default='0')
    surgery = fields.Boolean("Phẫu thuật hay xăm hình")
    surgery_content = fields.Char("Nội dung Phẫu thuật hay xăm hình")
    drink_alcohol = fields.Boolean("Uống rượu bia")
    specialized = fields.Char("Chuyên ngành")


    favourite = fields.Char("Sở thích")
    strong = fields.Char("Điểm mạnh")
    weak = fields.Char("Điểm yếu")
    teammate = fields.Boolean("Có kinh nghiệm sống tập thể",default=True)
    cooking = fields.Boolean("Biết nấu ăn",default=True)
    diseases = fields.Boolean("Tiền sử bệnh lý")


    note_health_vi = fields.Char('Ghi chú sức khỏe')
    surgery_content_vi = fields.Char('Nội dung Phẫu thuật hay xăm hình')
    specialized_vi = fields.Char("Chuyên ngành")
    favourite_vi = fields.Char("Sở thích")
    strong_vi = fields.Char("Điểm mạnh")
    weak_vi = fields.Char("Điểm yếu")
    family_income_vi = fields.Float("Tổng thu nhập gia đình", size=15, digits=(15, 0))
    motivation_vi = fields.Char("Lý do đi Nhật")
    income_after_three_year_vi = fields.Float("Sau 3 năm bạn muốn kiếm được bao nhiêu ?", size=15, digits=(15, 0))
    job_after_return_vi = fields.Char("Sau khi về nước bạn muốn làm công việc gì ?")
    prefer_object_vi = fields.Char("Nếu nhận mức lương gấp 3 hiện tại bạn muốn mua gì ?")
    memory_vi = fields.Char("Kỷ niệm đáng nhớ nhất của bạn")
    valuable_vi = fields.Char("Điều quý giá")
    family_member_in_jp_vi = fields.Char("Người thân ở Nhật")
    education_content_vi = fields.Char("Nội dung Tình trạng học tập")


    family_income = fields.Char("Tổng thu nhập gia đình")
    motivation = fields.Char("Lý do đi Nhật")
    income_after_three_year = fields.Char("Sau 3 năm bạn muốn kiếm được bao nhiêu ?")
    job_after_return = fields.Char("Sau khi về nước bạn muốn làm công việc gì ?")
    prefer_object = fields.Char("Nếu nhận mức lương gấp 3 hiện tại bạn muốn mua gì ?")
    memory = fields.Char("Kỷ niệm đáng nhớ nhất của bạn")
    valuable = fields.Char("Điều quý giá")

    def _get_education_status_list(self):
        if not self.env.context.get('jp', False):
            return [('1', 'Nhập học sớm'), ('2', 'Nhập học muộn'), ('3', 'Lưu ban')]
        return [('1', '年数過剰入学'), ('2', '年数不足入学'), ('3', '留年')]

    education_status = fields.Selection(_get_education_status_list, "Tình trạng học tập")
    education_content = fields.Char("Nội dung Tình trạng học tập")


    # intern_education =fields.Many2one('intern.education')
    # intern_employment_history =fields.Many2one('intern.employment')

    family_member_in_jp = fields.Char("Người thân ở Nhật")
    family_accept = fields.Boolean("Gia đình có đồng ý cho đi Nhật không?", default=True)




    # info = fields.Many2one('intern.info',"Sơ yếu lý lịch")



    # @api.model
    # def get_creator(self):
    #     return self.env['res.par'].search([('type', 'in', ['income', 'value', 'excise'])]).ids


    #
    # @api.multi
    # def write(self, vals):
    #     record = super(Intern, self).create(vals)
    #     record['name_without_signal'] = no_accent_vietnamese(record['name'])
    #     return record

    # @api.model
    # def load_views(self, views, options=None):
    #     _logger.info("AAAAAAAAAAAAA")
    #     for member in self.family_members:
    #         try:
    #             member.ages = (datetime.now().year) + 1 - member.birth_year
    #             _logger.info("AGE %d" % member.ages)
    #         except Exception ,e:
    #             _logger.info(e)
    #             member.ages = 0
    #     return super(Intern, self).load_views(views, options)

class InvoiceStt(models.Model):
    _name = 'intern.invoicestt'
    invoiceid = fields.Integer('Invoice_id')
    status = fields.Selection([(1,'Tiến cử'),(2,'Thi tuyển'),(3,'Trúng tuyển'),(4,'Xin TCLT'),(5,'Xin Visa'),(6,'Xuất cảnh')],'Trạng thái')
    canceled = fields.Boolean('Bị hủy',default=False)

class Intern(models.Model):
    _name = 'intern.intern'
    _inherits = {'intern.interndn': 'interndn_id', 'intern.internks': 'internks_id', 'intern.internhs': 'internhs_id'}

    _description = 'Thực tập sinh'
    _order = 'id desc'

    custom_id = fields.Char('Mã số')
    _sql_constraints = [('unique_id', 'UNIQUE(custom_id)', "Đã tồn tại TTS có mã số này"), ]

    educations = fields.One2many("intern.education", "info", string="Học tập")
    employments = fields.One2many("intern.employment", "info", string="Việc làm")
    family_members = fields.One2many("intern.family", "info", string="Gia đình")

    educations_vi = fields.One2many("intern.educationvi", "info", string="Lý lịch học tập")
    employments_vi = fields.One2many("intern.employmentvi", "info", string="Kinh nghiệm làm việc")
    family_members_vi = fields.One2many("intern.familyvi", "info", string="Gia đình")



    interndn_id = fields.Many2one('intern.interndn', required=True, ondelete='cascade', auto_join=True,
                                 string='Related Intern', help='Intern-related data of the user')

    internks_id = fields.Many2one('intern.internks', required=True, ondelete='cascade', auto_join=True,
                                  string='Related Intern', help='Intern-related data of the user')

    internhs_id = fields.Many2one('intern.internhs', required=True, ondelete='cascade', auto_join=True,
                                  string='Related Intern', help='Intern-related data of the user')

    # test = ["aa","bb"]
    # invoice_list_status = fields.Many2many('intern.invoicestt','lưu trạng thái tts ở mỗi đơn hàng')
    notice_name = fields.Char('Chú ý',store=False,compute='_calculate_name')
    #
    # company_id = fields.Integer("CompanyId")

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


    def convertToJP(self,name):
        words = name.split()
        final = ""
        for i,word in enumerate(words):
            jps = self.env['intern.translator'].search([('vi_word','=',word.upper())],limit=1)
            if jps:
                if i > 0:
                    final = final+u"・"
                final = final+jps[0].jp_word
            else:
                return ""
        return final

    @api.multi
    @api.onchange('logic_correct','logic_done')
    @api.depends('logic_correct', 'logic_done')
    def _cal_logic_percentage(self):
        for rec in self:
            if rec.logic_done is not 0:
                rec.logic_percentage = "%d" % (percentage(rec.logic_correct, rec.logic_done))

    @api.multi
    @api.onchange('add_correct', 'add_done')
    @api.depends('add_correct', 'add_done')
    def _cal_add_percentage(self):
        for rec in self:
            if rec.add_done is not 0:
                rec.add_percentage = "%d" % (percentage(rec.add_correct, rec.add_done))

    @api.multi
    @api.onchange('calculation_correct', 'calculation_done')
    @api.depends('calculation_correct', 'calculation_done')
    def _cal_calculation_percentage(self):
        for rec in self:
            if rec.calculation_done is not 0:
                rec.calculation_percentage = "%d" % (percentage(rec.calculation_correct, rec.calculation_done))

    @api.multi
    @api.onchange('notice_correct', 'notice_done')
    @api.depends('notice_correct', 'notice_done')
    def _cal_notice_percentage(self):
        for rec in self:
            if rec.notice_done is not 0:
                rec.notice_percentage = "%d" % (percentage(rec.notice_correct, rec.notice_done))

    @api.multi
    @api.onchange('logic_correct', 'add_correct','calculation_correct','notice_correct','total_question')
    @api.depends('logic_correct', 'add_correct', 'calculation_correct', 'notice_correct', 'total_question')
    def _cal_total_percentage(self):
        for rec in self:
            rec.total_correct = rec.logic_correct + rec.add_correct + rec.calculation_correct + rec.notice_correct
            if rec.total_question is not 0:
                rec.iq_percentage = "%d" % (percentage(rec.total_correct, rec.total_question))


    # @api.onchange('room_recruitment')
    # def _set_domain_for_recruitment_employee(self):
    #
    #     ids = []
    #     if self.room_recruitment:
    #         if self.room_recruitment.members:
    #             for member in self.room_recruitment.members:
    #                 ids.append(member.id)
    #         if self.room_recruitment.manager:
    #             ids.append(self.room_recruitment.manager.id)
    #
    #     return {'domain': {'recruitment_employee': [('id', 'in', ids)]}}

    show_specialized = fields.Boolean(store=False, default=False, compute='certification_change')

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



    @api.model
    def create(self, vals):

        if 'identity' not in vals and 'identity_2' not in vals:
            raise ValidationError('Bạn chưa nhập CMND hoặc thẻ căn cước')

        if 'identity' in vals and vals['identity']:
            vals['identity'] = vals['identity'].strip()
            tmp = self.env['intern.intern'].search([('identity', '=', vals['identity'])], limit=1)
            if tmp and len(tmp) == 1:
                raise ValidationError('Đã tồn tại TTS có số CMND này')

        if 'identity_2' in vals and vals['identity_2']:
            vals['identity_2'] = vals['identity_2'].strip()
            tmp = self.env['intern.intern'].search([('identity_2', '=', vals['identity_2'])], limit=1)
            if tmp and len(tmp) == 1:
                raise ValidationError('Đã tồn tại TTS có số thẻ căn cước này')

        if 'certification' in vals and 'educations' in vals:
            # _logger.info("AAAA %s %s"%(str(vals['certification']),str(vals['educations'])))
            contain_check = False
            specilization_check = False
            if not vals['certification'] or not vals['educations']:
                contain_check = True
                specilization_check = True
            if vals['certification'] == 1:  #THCS
                specilization_check = True
                for education in vals['educations']:
                    if 'certificate' in education[2] and education[2]['certificate'] == 2:
                        contain_check = True
                        break
            if vals['certification'] == 2:  # THPT
                specilization_check = True
                for education in vals['educations']:
                    if 'certificate' in education[2] and education[2]['certificate'] == 3:
                        contain_check = True
                        break
            if vals['certification'] == 3:  # Trung cap
                for education in vals['educations']:
                    # _logger.info("WTF %s"%str(vals))
                    if 'certificate' in education[2] and education[2]['certificate'] == 6:
                        contain_check = True
                        if 'specialized' in vals and 'specialization' in education[2]:
                            if education[2]['specialization'] and vals['specialized'] and vals['specialized'].upper() == education[2]['specialization'].upper():
                                specilization_check = True
                        else:
                            specilization_check = True
                        break
            if vals['certification'] == 4:  # Cao dang
                for education in vals['educations']:
                    if 'certificate' in education[2] and education[2]['certificate'] == 4:
                        contain_check = True
                        if 'specialized' in vals and 'specialization' in education[2]:
                            if education[2]['specialization'] and vals['specialized'] and vals['specialized'].upper() == education[2]['specialization'].upper():
                                specilization_check = True
                        else:
                            specilization_check = True
                        break
            if vals['certification'] == 5:  # Dai hoc
                for education in vals['educations']:
                    if 'certificate' in education[2] and education[2]['certificate'] == 5:
                        contain_check = True
                        if 'specialized' in vals and 'specialization' in education[2]:
                            if education[2]['specialization'] and vals['specialized'] and vals['specialized'].upper() == education[2]['specialization'].upper():
                                specilization_check = True
                        else:
                            specilization_check = True
                        break
            if not contain_check:
                raise ValidationError('Lý lịch học tập chưa tương ứng với trình độ học vấn')
            elif not specilization_check:
                raise ValidationError('Lý lịch học tập chưa tương ứng với chuyên ngành')

        # _logger.info("AAA------------ %s"%list(vals))

        # vals['company_id'] = self.env.user.company_id.id

        if 'enter_source' in vals:
            if vals['enter_source']!= False and vals['enter_source']!='4':
                # vals['date_enter_source'] = fields.date.today()
                vals['enter_source_tmp'] = vals['enter_source']


        record = super(Intern, self).create(vals)
        try:
            splitName = vals['name'].split()
            tempSplitName = intern_utils.fix_accent_2(intern_utils.no_accent_vietnamese2(vals['name'])).split()
            if u'・' in vals['name_in_japan']:
                tempSplitJp = vals['name_in_japan'].split(u'・')
            elif u' ' in vals['name_in_japan']:
                tempSplitJp = vals['name_in_japan'].split(u' ')
            else:
                tempSplitJp =[]

            if len(tempSplitName) == len(tempSplitJp):
                for i, s in enumerate(tempSplitName):
                    s = s.strip()
                    jps = self.env['intern.translator'].search([('vi_word', '=', s.upper())], limit=1)
                    if not jps:
                        # _logger.info("splitName[i] " + splitName[i] + "  " + tempSplitJp[i])
                        self.env['intern.translator'].create({
                            'vi_word': s.upper(), 'jp_word': tempSplitJp[i]
                        })
        except:
            print('Loi roi')

        return record

    @api.onchange('enter_source')
    def on_enter_source_change(self):
        if self.enter_source:
            if self.enter_source!='4':
                if not self.date_enter_source:
                    self.date_enter_source = fields.date.today()
                if self.date_escape_source:
                    self.date_escape_source = False
            else:
                if not self.date_escape_source:
                    self.date_escape_source = fields.date.today()
        else:
            self.enter_source_tmp = False
            self.date_enter_source = False
            self.date_escape_source = False

    @api.constrains('name_in_japan')
    def validate_name_in_japan(self):
        _logger.info("validate_name_in_japan")

        if self.name_in_japan and self.name:
            tempSplitName = self.name.split()
            tempSplitJp = self.name_in_japan.split(u'・')
            if len(tempSplitName) == len(tempSplitJp):
                return True
            else:
                if u'・' not in self.name_in_japan:
                    raise ValidationError(u'Tên tiếng Nhật của TTS chưa đúng. Lưu ý các chữ cách nhau bằng dấu ・')
                else:
                    raise ValidationError('Tên tiếng Nhật của TTS chưa đúng')
        return True

    # @api.constrains('identity')
    # def unique_identity(self):
    #     _logger.info("vao ")
    #
    @api.onchange('identity','identity_2')
    @api.multi
    def check_identity(self):
        for rec in self:
            if rec.identity:
                if type(rec.id) == int:
                    tmp = self.env['intern.intern'].search([('identity', '=', rec.identity), ('id', '!=', rec.id)], limit=1)
                    if tmp and len(tmp) == 1:
                        raise ValidationError('Đã tồn tại TTS có số CMND này')
                else:
                    tmp = self.env['intern.intern'].search([('identity', '=', rec.identity)],
                                                           limit=1)
                    if tmp and len(tmp) == 1:
                        raise ValidationError('Đã tồn tại TTS có số CMND này')

            elif rec.identity_2:
                if type(rec.id) == int:
                    tmp = self.env['intern.intern'].search([('identity_2', '=', rec.identity_2), ('id', '!=', rec.id)], limit=1)
                    if tmp and len(tmp) == 1:
                        raise ValidationError('Đã tồn tại TTS có số thẻ cc này')
                else:
                    tmp = self.env['intern.intern'].search([('identity_2', '=', rec.identity_2)],
                                                           limit=1)
                    if tmp and len(tmp) == 1:
                        raise ValidationError('Đã tồn tại TTS có số thẻ cc này')


    @api.one
    def write(self, vals):
        _logger.info("WRITE")
        if 'identity' in vals and vals['identity']:
            vals['identity'] = vals['identity'].strip()
            tmp = self.env['intern.intern'].search([('identity', '=', vals['identity']),('id','!=',self.id)], limit=1)

            if tmp and len(tmp) == 1:
                raise ValidationError('Đã tồn tại TTS có số CMND này')
        if 'identity_2' in vals and vals['identity_2']:
            vals['identity_2'] = vals['identity_2'].strip()
            tmp = self.env['intern.intern'].search([('identity_2', '=', vals['identity_2']),('id','!=',self.id)], limit=1)
            if tmp and len(tmp) == 1:
                raise ValidationError('Đã tồn tại TTS có số thẻ căn cước này')


        if 'certification' in vals and 'educations' in vals:
            # _logger.info("AAAA %s "%(str(vals)))
            contain_check = False
            specilization_check = False
            if not vals['certification'] or not vals['educations']:
                contain_check = True
                specilization_check = True

            if vals['certification'] == 1:  #THCS
                specilization_check = True
                for education in vals['educations']:
                    if education[2] and 'certificate' in education[2] and education[2]['certificate'] == 2:
                        contain_check = True
                        break
            if vals['certification'] == 2:  # THPT
                specilization_check = True
                for education in vals['educations']:
                    if education[2] and 'certificate' in education[2] and education[2]['certificate'] == 3:
                        contain_check = True
                        break
            if vals['certification'] == 3:  # Trung cap
                for education in vals['educations']:
                    if education[2] and 'certificate' in education[2] and education[2]['certificate'] == 6:
                        contain_check = True
                        if 'specialized' in vals and 'specialization' in education[2]:
                            if education[2]['specialization'] and vals['specialized'] and vals['specialized'] and vals['specialized'].upper() == education[2]['specialization'].upper():
                                specilization_check = True
                        else:
                            specilization_check = True
                        break
            if vals['certification'] == 4:  # Cao dang
                for education in vals['educations']:
                    if education[2] and 'certificate' in education[2] and education[2]['certificate'] == 4:
                        contain_check = True
                        if 'specialized' in vals and 'specialization' in education[2]:
                            if education[2]['specialization'] and vals['specialized'] and vals['specialized'] and vals['specialized'].upper() == education[2]['specialization'].upper():
                                specilization_check = True
                        else:
                            specilization_check = True
                        break
            if vals['certification'] == 5:  # Dai hoc
                for education in vals['educations']:
                    if education[2] and 'certificate' in education[2] and education[2]['certificate'] == 5:
                        contain_check = True
                        if 'specialized' in vals and 'specialization' in education[2]:
                            if education[2]['specialization'] and vals['specialized'] and vals['specialized'] and vals['specialized'].upper() == education[2]['specialization'].upper():
                                specilization_check = True
                        else:
                            specilization_check = True
                        break
            if not contain_check:
                raise ValidationError('Lý lịch học tập chưa tương ứng với trình độ học vấn')
            elif not specilization_check:
                raise ValidationError('Lý lịch học tập chưa tương ứng với chuyên ngành')

        if 'enter_source' in vals:
            if vals['enter_source']!= False and vals['enter_source'] != '4':
                # vals['date_enter_source'] = fields.date.today()
                vals['enter_source_tmp'] = vals['enter_source']
            # else:
                # intern = self.env['intern.intern'].browse(self.id)
                # if self.date_enter_source!= None and fields.date.today() - timedelta(days=7) < datetime.strptime(self.date_enter_source,'%Y-%m-%d').date():
                    # vals['date_enter_source'] = False
                    # vals['enter_source_tmp'] = False
                # else:
                #     vals['date_escape_source'] = fields.date.today()


        if vals.get('name_in_japan'):
            tempSplitName = intern_utils.fix_accent_2(intern_utils.no_accent_vietnamese2(self.name)).split()
            if u'・' in vals['name_in_japan']:
                tempSplitJp = vals['name_in_japan'].split(u'・')
            elif u' ' in vals['name_in_japan']:
                tempSplitJp = vals['name_in_japan'].split(u' ')
            else:
                tempSplitJp =[]
            if len(tempSplitName) == len(tempSplitJp):
                for i, s in enumerate(tempSplitName):
                    s = s.strip()
                    jps = self.env['intern.translator'].search([('vi_word', '=', s.upper())], limit=1)
                    if not jps:
                        # _logger.info("splitName[i] " + splitName[i] + "  " + tempSplitJp[i])
                        self.env['intern.translator'].create({
                            'vi_word': s.upper(), 'jp_word': tempSplitJp[i]
                        })

        # self.send_to_channel("TAO TEST TY","Log")
        super(Intern, self).write(vals)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()

        if name:
            recs = self.search([('name_without_signal', 'ilike', intern_utils.no_accent_vietnamese(name))] + args, limit=limit)
            if not recs:
                recs = self.search([('name_in_japan', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if domain is not None:
            _logger.info("DOMAIN %s"%str(domain))
            for x in domain:
                if x[0] == 'name':
                    x[0] = 'name_without_signal'
                    x[2] = intern_utils.no_accent_vietnamese(x[2])
                if x[0] == 'identity' and len(domain) == 1:
                    term = x[2]
                    domain = ['|',['identity','ilike',term],['identity_2','ilike',term]]
                    break
            _logger.info("DOMAIN %s" % str(domain))
        return super(Intern, self).search_read(domain, fields, offset, limit, order)


    #For handle sequence
    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=1000,store=False)

    @api.multi
    def _compute_identity(self):
        for rec in self:
            if rec.identity:
                rec.cmnd_or_tcc = rec.identity
            else:
                rec.cmnd_or_tcc = rec.identity_2

    #Tien cu
    cmnd_or_tcc = fields.Char("CMND/Thẻ CC",store=False,compute=_compute_identity)
    have_form = fields.Boolean(string="Có Form")
    have_health = fields.Boolean(string="Có giấy khám SK")
    have_deposit = fields.Boolean(string="Đặt cọc")



    @api.multi
    def _count_condition(self):
        for rec in self:
            rec.condition_count = 0
            if rec.have_form:
                rec.condition_count = rec.condition_count+5
            if rec.have_health:
                rec.condition_count = rec.condition_count + 5
            if rec.have_deposit:
                rec.condition_count = rec.condition_count + 5
            if rec.avatar:
                rec.condition_count = rec.condition_count + 5

    condition_count = fields.Integer("",store=False,compute=_count_condition)


    # def send_to_channel(self, body, ch_name):
    #     ch_obj = self.env['mail.channel']
    #     ch = ch_obj.sudo().search([('name', 'ilike', str(ch_name))])
    #
    #     ch.message_post(attachment_ids=[], body=body, content_subtype='html',
    #
    #                     message_type='comment', partner_ids=[], subtype='mail.mt_comment',
    #
    #                     email_from=self.env.user.partner_id.email, author_id=self.env.user.partner_id.id)
    #
    #     return True

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(Intern, self).read(fields, load)
        return result

    recruitment_r_employee = fields.Many2one('hh.employee', string=u"Cán bộ phụ trách thực tế")

    discipline = fields.One2many('intern.discipline', 'intern_id', string='Bị kỷ luật')
    deportation = fields.Boolean('Bị đuổi học')

    exp_sew = fields.Boolean('Tay nghề may')
    exp_mechanical = fields.Boolean('Tay nghề cơ khí,hàn')
    exp_building = fields.Boolean('KN xây dựng')
    exp_note = fields.Text('Ghi chú tay nghề')

    date_of_birth_short = fields.Date("Ngày sinh", store=True, compute='_date_of_birth_short')

    @api.multi
    @api.depends('day', 'month', 'year')
    def _date_of_birth_short(self):
        for rec in self:
            if rec.day and rec.month and rec.year:
                rec.date_of_birth_short = datetime.strptime('%s-%s-%s' % (rec.year, rec.month, rec.day), '%Y-%m-%d')
            else:
                rec.date_of_birth_short = None


    current_status = fields.Char("Trạng thái",store=False, compute='_compute_status')

    @api.multi
    def _compute_status(self):
        for obj in self:
            self._cr.execute(
                "SELECT * FROM intern_internclone WHERE intern_internclone.intern_id = %d AND COALESCE(intern_internclone.cancel_exam, FALSE) = FALSE AND intern_internclone.create_date > now()::date - interval '3 y'" % obj['id'])
            tmpresult = self._cr.dictfetchall()
            promoteds = []
            exams = []
            for record in tmpresult:
                if record['departure'] and not record['comeback']:
                    obj.current_status = 'Đã xuất cảnh'
                    break
                if record['pass_exam'] and record['done_exam']:
                    obj.current_status = 'Đã trúng tuyển'
                    break
                if record['confirm_exam'] and not record['done_exam']:
                    # obj.current_status = 'Đã chốt thi'
                    # break
                    invoice = self.env['intern.invoice'].browse(record['invoice_id'])
                    if invoice:
                        exams.append(invoice.name)
                if record['promoted'] and not record['done_exam']:
                    # obj.current_status = 'Đang tiến cử'
                    invoice = self.env['intern.invoice'].browse(record['invoice_id'])
                    if invoice:
                        promoteds.append(invoice.name)
                    # break
            if len(exams)>0:
                obj.current_status = u'Đã chốt thi đơn %s'%(', '.join(exams))
            elif len(promoteds) >0:
                obj.current_status = u'Đang tiến cử đơn %s' % (', '.join(promoteds))

    passport_no = fields.Char('Passport No.')
    passport_type = fields.Selection([('0','Ngoại giao'),('1','Công vụ'),('2','Phổ thông'),('3','Khác')],string='Loại passport')
    passport_place = fields.Many2one('province',string="Nơi cấp")
    passport_date_issue = fields.Date(string='Ngày cấp')
    passport_issuing_authority = fields.Char('Cơ quan cấp')
    passport_date_expire = fields.Date('Ngày hết hạn')

    # go_abroad = fields.One2many("intern.abroad", "info")

    had_go_abroad = fields.Boolean('Đã từng đi nước ngoài')
    country_go_abroad = fields.Char('Nước nào')
    year_go_abroad = fields.Char('Năm nào')

    had_visa_jp = fields.Boolean('Đã từng xin VISA đi Nhật')