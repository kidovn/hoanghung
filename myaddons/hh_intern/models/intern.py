# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime
from odoo.addons.payment.models.payment_acquirer import ValidationError
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


class InternEducation(models.Model):
    _name = 'intern.education'
    info = fields.Many2one("intern.intern", required=True,ondelete='cascade')

    month_start = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_start = fields.Char("Năm bắt đầu", size=4)

    month_end = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")
    year_end = fields.Char("Năm kết thúc", size=4)

    school = fields.Char("Tên trường",required=True)
    school_type = fields.Many2one("school")
    specialization = fields.Char("Chuyên ngành")
    certificate = fields.Many2one("school","Bằng cấp")
    graduated = fields.Boolean("Đã tốt nghiệp", default= True)
    show_specialization = fields.Boolean(store=False)

    @api.onchange('school_type')  # if these fields are changed, call method
    def school_type_change(self):
        if self.school_type:
            if self.school_type.name_in_vn == u'Tiểu học':
                self.specialization = self.school_type.name_in_jp
                self.show_specialization = False
            elif self.school_type.name_in_vn == u'Trung học cơ sở':
                self.specialization = self.school_type.name_in_jp
                self.show_specialization = False
            elif self.school_type.name_in_vn == u'Trung học phổ thông':
                self.specialization = self.school_type.name_in_jp
                self.show_specialization = False
            else:
                self.specialization = ""
                self.show_specialization = True
            self.certificate = self.school_type
        else:
            self.show_specialization = False





class InternEmployment(models.Model):
    _name = 'intern.employment'
    info = fields.Many2one("intern.intern",required=True,ondelete='cascade')
    month_start = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_start = fields.Char("Năm bắt đầu", size=4,required=True)

    month_end = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")
    year_end = fields.Char("Năm kết thúc", size=4,required=True)

    company = fields.Char("Tên công ty",required=True)
    description = fields.Char("Lý lịch làm việc")

class InternFamily(models.Model):
    _name = 'intern.family'
    info = fields.Many2one("intern.intern", required=True,ondelete='cascade')
    name = fields.Char("Tên",required=True)
    relationship = fields.Char("Quan hệ",required=True)
    ages = fields.Integer("Tuổi", store=False,required =True)
    birth_year = fields.Integer("Năm sinh")
    # birth_year = fields.Selection([(num, str(num)) for num in reversed(range(1900, (datetime.now().year)+1 ))],"Năm sinh",required=True)
    job = fields.Char("Nghề nghiệp")
    live_together = fields.Boolean("Sống chung")

    @api.onchange('ages')  # if these fields are changed, call method
    def name_change(self):
        if self.name:
            self.birth_year = (datetime.now().year) - self.ages

    # @api.one
    # def _get_ages(self):
    #     try:
    #         self.ages = (datetime.now().year)+1 - self.birth_year
    #     except:
    #         self.ages = 0

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(InternFamily,self).read(fields,load)
        for record in result:
            if 'birth_year' in record and 'ages' in record:
                record['ages'] = datetime.now().year - record['birth_year']
        return result


def percentage(part, whole):
    return 100 * float(part)/float(whole)

class InternKS(models.Model):
    _name = 'intern.internks'
    _description = 'Thực tập sinh'

    serial = fields.Char("Mã số")
    long_term = fields.Boolean("Đăng ký dài hạn")

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

    name = fields.Char("Tên tiếng Việt có dấu", required=True)

    gender = fields.Selection([('nam', 'Nam'), ('nu', 'Nữ')])
    day = fields.Char("Ngày", size=2)
    month = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year = fields.Char("Năm", size=4)

    date_of_birth = fields.Char("Ngày sinh", store=False, compute='_date_of_birth')

    name_without_signal = fields.Char("Tên tiếng Việt ko dấu")
    name_in_japan = fields.Char("Tên tiếng Nhật")

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
    relative_note = fields.Many2one('relation',string='Quan hệ')

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
    logic_percentage = fields.Char(store=False,compute='_cal_logic_percentage')

    @api.one
    def _cal_logic_percentage(self):
        _logger.info("VAO_cal_logic_percentage")
        if self.logic_done is not 0:
            self.logic_percentage = "%d" % (percentage(self.logic_correct, self.logic_done))


    add_correct = fields.Integer()
    add_done = fields.Integer()
    add_percentage = fields.Char(store=False,compute='_cal_add_percentage')

    @api.one
    def _cal_add_percentage(self):
        if self.add_done is not 0:
            self.add_percentage = "%d"%(percentage(self.add_correct,self.add_done))

    calculation_correct = fields.Integer()
    calculation_done = fields.Integer()
    calculation_percentage = fields.Char(store=False,compute='_cal_calculation_percentage')

    @api.one
    def _cal_calculation_percentage(self):
        if self.calculation_done is not 0:
            self.calculation_percentage ="%d"%(percentage(self.calculation_correct,self.calculation_done))

    notice_correct = fields.Integer()
    notice_done = fields.Integer()
    notice_percentage = fields.Char(store=False,compute='_cal_notice_percentage')

    @api.one
    def _cal_notice_percentage(self):
        if self.notice_done is not 0:
            self.notice_percentage ="%d"%(percentage(self.notice_correct,self.notice_done))

    total_correct = fields.Integer(store=False,compute='_cal_total_corect')
    total_question = fields.Integer("Tổng số câu", default=133)
    iq_percentage = fields.Char("Trung bình cộng"
                                ,compute='_cal_total_percentage'
                                )

    @api.multi
    def _cal_total_corect(self):
        for rec in self:
            rec.total_correct = rec.logic_correct + rec.add_correct + rec.calculation_correct + rec.notice_correct
        # _logger.info("Total_percentage " + str(self.total_correct) + " " + str(self.total_question))
        # if self.total_question is not 0:
        #     self.total_percentage = "%d" % (percentage(self.total_correct, self.total_question))
        #     _logger.info("PEE" + self.total_percentage)

    @api.multi
    def _cal_total_percentage(self):
        for rec in self:
            if rec.total_question is not 0:
                rec.iq_percentage = "%d" % (percentage(rec.total_correct, rec.total_question))

    employments_vi = fields.One2many("intern.employment", "info", string="Kinh nghiệm làm việc")

    average = fields.Float(u"Trung bình cộng", store=False)
    incremental = fields.Integer(u"Cộng dồn")

    # room_recruitment = fields.Many2one("department",string=u"Phòng tuyển dụng")
    # recruitment_employee = fields.Many2one('hh.employee',string=u"Cán bộ tuyển dụng")
    room_recruitment = fields.Char(string=u"Phòng tuyển dụng")
    recruitment_employee = fields.Char(string=u"Cán bộ tuyển dụng")

    pass_recruitment = fields.Selection([('0','Thanh lý'),('1','Trúng tuyển')],string="Trúng tuyển")
    # pass_recruitment = fields.Selection([(0,'Thanh lý'),(1,'Trúng tuyển')],string="Trúng tuyển")


    invoice_name_vi = fields.Char(u'Đơn hàng')

    promotions = fields.One2many("intern.promotion", "intern", string=u"Tiến cử")


    #pass
    day_pass = fields.Char("Ngày", size=2)
    month_pass = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")
    year_pass = fields.Char("Năm", size=4,default=lambda self: self._get_current_year())

    date_pass = fields.Char("Ngày gửi hồ sơ", store=False, compute='_date_pass',)

    @api.multi
    @api.depends('day_pass', 'month_pass', 'year_pass')
    def _date_pass(self):
        for rec in self:
            if rec.day_pass and rec.month_pass and rec.year_pass:
                rec.date_pass = u"%s Tháng %s Năm %s" % (rec.day_pass, rec.month_pass, rec.year_pass)
            else:
                rec.date_pass =""


    fee_departure = fields.Char(u"Phí xuất cảnh")
    syndication = fields.Char(u"Nghiệp đoàn")
    place_to_work = fields.Char(u"Địa điểm làm việc")


    #ngay nhap hoc
    day_join_school = fields.Char("Ngày", size=2)
    month_join_school = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_join_school = fields.Char("Năm", size=4,default=lambda self: self._get_current_year())

    date_join_school = fields.Char("Ngày nhập học", store=False, compute='_date_join_school')

    @api.multi
    @api.depends('day_join_school', 'month_join_school', 'year_join_school')
    def _date_join_school(self):
        for rec in self:
            if rec.day_join_school and rec.month_join_school and rec.year_join_school:
                rec.date_join_school = u"%s Tháng %s Năm %s" % (rec.day_join_school, rec.month_join_school, rec.year_join_school)
            else:
                rec.date_join_school = ""

    #du kien xuat canh
    day_leave = fields.Char("Ngày", size=2)
    month_leave = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_leave = fields.Char("Năm", size=4,default=lambda self: self._get_current_year())

    date_leave = fields.Char("Ngày gửi hồ sơ", store=False, compute='_date_leave')

    @api.multi
    @api.depends('day_leave', 'month_leave', 'year_leave')
    def _date_leave(self):
        for rec in self:
            if rec.day_leave and rec.month_leave and rec.year_leave:
                rec.date_leave = u"%s Tháng %s Năm %s" % (rec.day_leave, rec.month_leave, rec.year_leave)
            else:
                rec.date_leave = ""

    # pttt_employee = fields.Many2one('hh.employee',string=u"Cán bộ phát triển thị trường", domain=[('room_type','=',1)])
    pttt_employee = fields.Char(string=u"Cán bộ PTTT")
    pttt_room = fields.Char(string=u"Phòng PTTT")

    legal_name = fields.Selection([('chauhung','Châu Hưng'),('hoanghung','Hoàng Hưng'),('tracodi','Tracodi')],'Pháp nhân')

    # thanh ly
    day_liquidation = fields.Char("Ngày", size=2)
    month_liquidation = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_liquidation = fields.Char("Năm", size=4,default=lambda self: self._get_current_year())


    liquidation_reason = fields.Selection([('0','Do thực tập sinh'),('1','Do Công ty'),('2','Do khách hàng')],string=u"Lý do thanh lý")
    liquidation_note = fields.Char("Nội dung")

    date_liquidation = fields.Char("Ngày gửi hồ sơ", store=False, compute='_date_liquidation')

    @api.multi
    @api.depends('day_liquidation', 'month_liquidation', 'year_liquidation')
    def _date_liquidation(self):
        for rec in self:
            if rec.day_liquidation and rec.month_liquidation and rec.year_liquidation:
                rec.date_liquidation = u"%s Tháng %s Năm %s" % (rec.day_liquidation, rec.month_liquidation, rec.year_liquidation)
            else:
                rec.date_liquidation =""

    user_access = fields.Many2many("res.users",default=lambda self: self.env.user, string="User có quyền xem")



class InternDN(models.Model):
    _name = 'intern.interndn'
    # _inherits = {'intern.internks': 'intern_id'}

    _description = 'Thực tập sinh'

    # intern_id = fields.Many2one('intern.internks', required=True, ondelete='restrict', auto_join=True,
    #                              string='Related Intern', help='Intern-related data of the user')


    blindness = fields.Boolean("Bệnh mù màu")
    smoking = fields.Boolean("Có hút thuốc")
    preferred_hand = fields.Selection((('0', 'Tay phải'), ('1', 'Tay trái')), string="Tay thuận", default='0')
    surgery = fields.Boolean("Phẫu thuật hay xăm hình")
    surgery_content = fields.Char("Nội dung")
    drink_alcohol = fields.Boolean("Uống rượu bia")
    specialized = fields.Char("Chuyên ngành")
    favourite = fields.Char("Sở thích")
    strong = fields.Char("Điểm mạnh")
    weak = fields.Char("Điểm yếu")
    teammate = fields.Boolean("Có kinh nghiệm sống tập thể")
    cooking = fields.Boolean("Biết nấu ăn")
    diseases = fields.Boolean("Tiền sử bệnh lý")




    family_income = fields.Char("Tổng thu nhập gia đình")
    motivation = fields.Char("Động lực")
    income_after_three_year = fields.Char("Sau 3 năm bạn muốn kiếm được bao nhiêu ?")
    job_after_return = fields.Char("Sau khi về nước bạn muốn làm công việc gì ?")
    prefer_object = fields.Char("Nếu nhận mức lương gấp 3 hiện tại bạn muốn mua gì ?")
    memory = fields.Char("Kỷ niệm đáng nhớ nhất của bạn")
    valuable = fields.Char("Điều quý giá")

    education_status = fields.Selection([('1', '年数過剰入学 '), ('2', '年数不足入学'), ('3', '留年')], "Tình trạng học tập")
    education_content = fields.Char("Nội dung")

    educations = fields.One2many("intern.education", "info",string="Học tập")
    employments = fields.One2many("intern.employment", "info",string="Việc làm")
    family_members = fields.One2many("intern.family", "info",string="Gia đình")
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

    interndn_id = fields.Many2one('intern.interndn', required=True, ondelete='restrict', auto_join=True,
                                 string='Related Intern', help='Intern-related data of the user')

    internks_id = fields.Many2one('intern.internks', required=True, ondelete='restrict', auto_join=True,
                                  string='Related Intern', help='Intern-related data of the user')

    internhs_id = fields.Many2one('intern.internhs', required=True, ondelete='restrict', auto_join=True,
                                  string='Related Intern', help='Intern-related data of the user')

    # test = ["aa","bb"]
    # invoice_list_status = fields.Many2many('intern.invoicestt','lưu trạng thái tts ở mỗi đơn hàng')
    notice_name = fields.Char('Chú ý',store=False,compute='_calculate_name')

    @api.depends('name')
    def _calculate_name(self):
        self.notice_name = ""
        if self.name:
            tmpName = intern_utils.fix_accent_2(intern_utils.no_accent_vietnamese2(self.name))
            words = tmpName.split()
            for i, word in enumerate(words):
                jps = self.env['intern.translator'].search([('vi_word', '=', word.upper())], limit=1)
                if not jps:
                    self.notice_name = "Một số từ trong tên TTS không có trong từ điển, vui lòng nhập tên tiếng Nhật của TTS"
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
                rec.total_percentage = "%d" % (percentage(rec.total_correct, rec.total_question))


    @api.onchange('room_recruitment')
    def _set_domain_for_recruitment_employee(self):

        ids = []
        if self.room_recruitment:
            if self.room_recruitment.members:
                for member in self.room_recruitment.members:
                    ids.append(member.id)
            if self.room_recruitment.manager:
                ids.append(self.room_recruitment.manager.id)

        return {'domain': {'recruitment_employee': [('id', 'in', ids)]}}

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
        _logger.info("CREATE")

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

        super(Intern, self).write(vals)