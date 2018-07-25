# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
import intern_utils
_logger = logging.getLogger(__name__)

class InternEducation(models.Model):
    _name = 'intern.education'
    info = fields.Many2one("intern.intern", required=True,ondelete='cascade',index=True)

    month_start = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng", default='09')

    year_start = fields.Char("Năm bắt đầu", size=4,required=True)

    month_end = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng",default='06')
    year_end = fields.Char("Năm kết thúc", size=4,required=True)

    school = fields.Char("Tên trường",required=True)
    school_type = fields.Many2one("school",required=True)
    specialization = fields.Char("Chuyên ngành",required=True)
    certificate = fields.Many2one("school","Bằng cấp")
    graduated = fields.Boolean("Đã tốt nghiệp", default= True)
    show_specialization = fields.Boolean(store=False)

    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=10)

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
    info = fields.Many2one("intern.intern",required=True,ondelete='cascade',index=True)
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
    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=10)


class InternFamily(models.Model):
    _name = 'intern.family'
    info = fields.Many2one("intern.intern", required=True,ondelete='cascade',index=True)
    name = fields.Char("Tên",required=True)
    relationship = fields.Char("Quan hệ",required=True)
    ages = fields.Integer("Tuổi", store=False)
    birth_year = fields.Integer("Năm sinh")
    # birth_year = fields.Selection([(num, str(num)) for num in reversed(range(1900, (datetime.now().year)+1 ))],"Năm sinh",required=True)
    job = fields.Char("Nghề nghiệp")
    live_together = fields.Boolean("Sống chung")

    @api.onchange('ages')  # if these fields are changed, call method
    def age_change(self):
        if self.ages:
            self.birth_year = (datetime.now().year) - self.ages
        else:
            self.birth_year = 0

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

    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=10)



# class Abroad(models.Model):
#     _name = 'intern.abroad'
#
#     info = fields.Many2one("intern.intern", required=True, ondelete='cascade')
#     country = fields.Char('Tên nước',required=True)
#
#     month_start = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
#                                     ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
#                                     ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")
#
#     year_start = fields.Char("Năm bắt đầu", size=4)
#
#     month_end = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
#                                   ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
#                                   ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")
#     year_end = fields.Char("Năm kết thúc", size=4)