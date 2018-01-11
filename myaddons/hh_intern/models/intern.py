# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime
from odoo.addons.payment.models.payment_acquirer import ValidationError
import intern_utils
import province
_logger = logging.getLogger(__name__)




class InternEducation(models.Model):
    _name = 'intern.education'
    info = fields.Many2one("intern.intern", required=True,ondelete='cascade')

    month_start = fields.Selection([(1, '01'), (2, '02'), (3, '03'), (4, '04'),
                              (5, '05'), (6, '06'), (7, '07'), (8, '08'),
                              (9, '09'), (10, '10'), (11, '11'), (12, '12'), ], "Tháng")

    year_start = fields.Char("Năm bắt đầu", size=4)

    month_end = fields.Selection([(1, '01'), (2, '02'), (3, '03'), (4, '04'),
                                    (5, '05'), (6, '06'), (7, '07'), (8, '08'),
                                    (9, '09'), (10, '10'), (11, '11'), (12, '12'), ], "Tháng")
    year_end = fields.Char("Năm kết thúc", size=4)

    school = fields.Char("Tên trường",required=True)
    school_type = fields.Many2one("school")
    specialization = fields.Text("Chuyên ngành")
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

    month_start = fields.Selection([(1, '01'), (2, '02'), (3, '03'), (4, '04'),
                                    (5, '05'), (6, '06'), (7, '07'), (8, '08'),
                                    (9, '09'), (10, '10'), (11, '11'), (12, '12'), ], "Tháng")

    year_start = fields.Char("Năm bắt đầu", size=4)

    month_end = fields.Selection([(1, '01'), (2, '02'), (3, '03'), (4, '04'),
                                  (5, '05'), (6, '06'), (7, '07'), (8, '08'),
                                  (9, '09'), (10, '10'), (11, '11'), (12, '12'), ], "Tháng")
    year_end = fields.Char("Năm kết thúc", size=4)

    company = fields.Text("Tên công ty",required=True)
    description = fields.Text("Lý lịch làm việc")

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
            self.birth_year = (datetime.now().year)+1 - self.ages

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
                record['ages'] = datetime.now().year+1 - record['birth_year']
        return result



class Intern(models.Model):
    _name = 'intern.intern'
    _description = 'Thực tập sinh'

    name = fields.Char("Tên tiếng Việt có dấu",required=True)
    name_without_signal = fields.Char("Tên tiếng Việt ko dấu")
    name_in_japan = fields.Char("Tên tiếng Nhật")
    gender = fields.Selection([('nam','Nam'),('nu','Nữ')])
    day = fields.Char("Ngày", size=2)
    month = fields.Selection([(1, '01'), (2, '02'), (3, '03'), (4, '04'),
                              (5, '05'), (6, '06'), (7, '07'), (8, '08'),
                              (9, '09'), (10, '10'), (11, '11'), (12, '12'), ],"Tháng")

    year = fields.Char("Năm",size=4)

    date_of_birth = fields.Char("Ngày sinh",store=False, compute='_date_of_birth')

    @api.one
    @api.depends('day', 'month','year')
    def _date_of_birth(self):
        self.date_of_birth = "%s/%s/%s"%(self.day,self.month,self.year)


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
    address = fields.Text('Địa chỉ liên hệ')
    province = fields.Many2one("province",string="Tỉnh/TP")
    avatar = fields.Binary("Ảnh")


    marital_status = fields.Many2one('marital', string="Tình trạng hôn nhân")
    height = fields.Integer("Chiều cao (cm)")
    weight = fields.Integer("Cân nặng (kg)")
    vision_left = fields.Char("Mắt trái")
    vision_right = fields.Char("Mắt phải")
    blindness = fields.Boolean("Bệnh mù màu")
    smoking = fields.Boolean("Có hút thuốc")
    preferred_hand = fields.Selection((('0', 'Tay phải'), ('1', 'Tay trái')), string="Tay thuận", default='0')
    surgery = fields.Boolean("Phẫu thuật hay xăm hình")
    surgery_content = fields.Char("Nội dung")
    drink_alcohol = fields.Boolean("Uống rượu bia")
    certification = fields.Many2one('intern.certification', "Bằng cấp")
    specialized = fields.Text("Chuyên ngành")
    favourite = fields.Text("Sở thích")
    strong = fields.Text("Điểm mạnh")
    weak = fields.Text("Điểm yếu")
    teammate = fields.Boolean("Có kinh nghiệm sống tập thể")
    cooking = fields.Boolean("Biết nấu ăn")
    diseases = fields.Boolean("Lý lịch bệnh tật")
    blood_group = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O')], 'Nhóm máu')
    check_kureperin = fields.Selection([('A+', 'A+'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
                                       "Kiểm tra kureperin")
    check_iq = fields.Char("Kiểm tra IQ")
    family_income = fields.Char("Tổng thu nhập gia đình")
    motivation = fields.Text("Động lực")
    income_after_three_year = fields.Char("Sau 3 năm bạn muốn kiếm được bao nhiêu ?")
    job_after_return = fields.Text("Sau khi về nước bạn muốn làm công việc gì ?")
    prefer_object = fields.Text("Nếu nhận mức lương gấp 3 hiện tại bạn muốn mua gì ?")
    memory = fields.Text("Kỷ niệm đáng nhớ nhất của bạn")
    valuable = fields.Text("Điều quý giá")

    education_status = fields.Selection([('1', '年数過剰入学 '), ('2', '年数不足入学'), ('3', '留年')], "Tình trạng học tập")
    education_content = fields.Char("Nội dung")

    educations = fields.One2many("intern.education", "info",string="Học tập")
    employments = fields.One2many("intern.employment", "info",string="Việc làm")
    family_members = fields.One2many("intern.family", "info",string="Gia đình")
    # intern_education =fields.Many2one('intern.education')
    # intern_employment_history =fields.Many2one('intern.employment')

    family_member_in_jp = fields.Char("Người thân ở Nhật")
    family_accept = fields.Boolean("Gia đình có đồng ý cho đi Nhật không?", default=True)

    user_access = fields.Many2many("res.users",default=lambda self: self.env.user, string="User có quyền xem")

    show_specialized = fields.Boolean(store=False,default=False)

    @api.multi
    @api.onchange('certification')  # if these fields are changed, call method
    def certification_change(self):
        if self.certification:
            if self.certification.id == 1:
                self.specialized = u'無し'
                self.show_specialized = False

            elif self.certification.id == 2:
                self.specialized = u'無し'
                self.show_specialized = False
            else:
                self.specialized = ""
                self.show_specialized = True
        else:
            self.show_specialized = False

    # info = fields.Many2one('intern.info',"Sơ yếu lý lịch")

    @api.model
    def create(self, vals):
        record = super(Intern, self).create(vals)
        try:
            splitName= vals['name'].split()
            tempSplitName = intern_utils.fix_accent_2(intern_utils.no_accent_vietnamese2(vals['name'])).split()
            tempSplitJp = vals['name_in_japan'].split(u'・')
            for i, s in enumerate(tempSplitName):
                s = s.strip()
                jps = self.env['intern.translator'].search([('vi_word', '=', s.upper())],limit=1)
                if not jps:
                    _logger.info("splitName[i] " + splitName[i] + "  " + tempSplitJp[i])
                    self.env['intern.translator'].create({
                        'vi_word': s.upper(), 'jp_word': tempSplitJp[i]
                    })
        except:
            print('Loi roi')

        return record

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
                return None
        return final


class InternKS(models.Model):
    _inherit = 'intern.intern'
    _name = 'intern.internks'
    _description = 'Thực tập sinh'

