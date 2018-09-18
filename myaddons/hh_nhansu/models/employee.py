# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import calendar

class Employee(models.Model):
    _inherit = 'hh.employee'

    # active = fields.Boolean(string='',track_visibility='onchange', default=True,
    #              help="If the active field is set to False, it will allow you to hide the resource record without removing it.")

    phone = fields.Char('Số điện thoại')
    work_email = fields.Char('Email')

    job_id = fields.Many2one('hh.job', string='Chức danh')
    identity = fields.Char('Số CMND')

    @api.onchange('identity')
    @api.multi
    def check_identity(self):
        for rec in self:
            if rec.identity:
                if type(rec.id) == int:
                    tmp = self.env['intern.intern'].search([('identity', '=', rec.identity), ('id', '!=', rec.id)],
                                                           limit=1)
                    if tmp and len(tmp) == 1:
                        raise ValidationError('Đã tồn tại TTS có số CMND này')
                else:
                    tmp = self.env['intern.intern'].search([('identity', '=', rec.identity)],
                                                           limit=1)
                    if tmp and len(tmp) == 1:
                        raise ValidationError('Đã tồn tại TTS có số CMND này')

    _sql_constraints = [('unique_identity', 'UNIQUE(identity)', "Đã tồn tại nhân viên có số CMND này"), ]

    date_identity = fields.Date('Ngày cấp')
    place_cmnd = fields.Many2one("province", string="Nơi cấp")

    ssnid = fields.Char('Mã số thuế', help='Social Security Number')
    sinid = fields.Char('Số sổ BHXH', help='Social Insurance Number')

    date_temp_work = fields.Date('Ngày bắt đầu thử việc')
    date_sign_offical_contract = fields.Date('Ngày ký hợp đồng chính thức')

    @api.multi
    @api.onchange('date_temp_work')
    def onchange_date_temp_work(self):
        for rec in self:
            if rec.date_temp_work:
                rec.date_sign_offical_contract = datetime.strptime(rec.date_temp_work,'%Y-%m-%d') + relativedelta(months=2)


    total_month_work = fields.Integer('Số tháng làm việc',store=False)
    total_year_work = fields.Integer('Số năm làm việc',store=False)

    date_start_offical = fields.Date('Thời hạn HĐ từ')
    date_end_offical = fields.Date('Thời hạn HĐ đến')

    bank_account_id = fields.Many2one('employee.bankaccount', string='Tài khoản')

    place_born = fields.Char('Nơi sinh')
    home_town = fields.Char('Nguyên quán')
    address = fields.Char('Hộ khẩu TT')
    folk = fields.Char('Dân tộc')
    religion = fields.Char('Tôn giáo')
    specialized = fields.Char("Chuyên ngành")
    certification = fields.Many2one('intern.certification', "Trình độ")
    school = fields.Char('Trường')

    members = fields.One2many('hh.familymember','info',string='Gia đình')



    date_resign = fields.Date('Ngày nghỉ thực tế')
    date_confirm_resign = fields.Date('Ngày duyệt nghỉ')

    active_custom = fields.Boolean(compute='_compute_active_custom',string='Đang làm việc')

    @api.multi
    def _compute_active_custom(self):
        for rec in self:
            rec.active_custom = rec.active


    birth_month = fields.Integer('Tháng sinh', compute = '_compute_birth_month',store=True)

    # date_of_birth_txt = fields.Char('Ngày sinh(dd/mm/yyyy)',store=True,compute='_compute_date_of_birth_txt')

    # @api.multi
    # def _compute_date_of_birth_txt(self):
    #     for rec in self:
    #         if rec.date_of_birth:
    #             rec.date_of_birth_txt = datetime.strptime(rec.date_of_birth,'%Y-%m-%d').strftime('%d-%m-%Y')
    #
    # @api.model
    # def create(self,vals):
    #     if 'date_of_birth_txt' in vals:
    #         vals['date_of_birth'] = datetime.strptime(vals['date_of_birth_txt'],'%d-%m-%Y')
    #     return super(Employee, self).create(vals)
    #
    # @api.multi
    # def write(self, vals):
    #     if vals.get('date_of_birth_txt'):
    #         vals['date_of_birth'] = datetime.strptime(vals['date_of_birth_txt'], '%d-%m-%Y')
    #         return super(Employee, self).write(vals)


    @api.multi
    @api.depends('date_of_birth')
    def _compute_birth_month(self):
        for rec in self:
            if rec.date_of_birth:
                rec.birth_month = datetime.strptime('%s'%rec.date_of_birth,'%Y-%m-%d').month
            else:
                rec.birth_month = False

    note = fields.Char('Ghi chú')

    # is_current_month = fields.Boolean(compute="_check_current_month", default=False)
    #
    # @api.depends('date_of_birth')
    # def _check_current_month(self):
    #     for rec in self:
    #         if rec.date_of_birth:
    #             first_day = date.today().replace(day=1)
    #             last_day = date.today().replace(
    #                 day=calendar.monthrange(date.today().year, date.today().month)[1])
    #             cur_date = datetime.strptime(rec.date_of_birth, '%Y-%m-%d %H:%M:%S').date()
    #             if first_day <= cur_date <= last_day:
    #                 rec.is_current_month = True
    #             else:
    #                 rec.is_current_month = False
    #         else:
    #             rec.is_current_month = False

class BankAccount(models.Model):
    _name = 'employee.bankaccount'
    name = fields.Char('Số tài khoản',required=True)

    account_holder = fields.Char('Tên chủ TK')

    bank_name = fields.Char('Ngân hàng')

    bank_branch = fields.Char('Chi nhánh')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Số tài khoản đã tồn tại'),
    ]

class Job(models.Model):
    _name = 'hh.job'
    name = fields.Char('Chức danh')
    department_id = fields.Many2one('department',string="Phòng")

class FamilyMember(models.Model):
    _name = 'hh.familymember'
    info = fields.Many2one("hh.employee", required=True, ondelete='cascade')
    name = fields.Char('Họ tên')
    age = fields.Integer("Tuổi", store=False)
    birth_year = fields.Char("Năm sinh")

    relationship = fields.Selection([('vo','Vợ'),('chong','Chồng'),('bo','Bố'),('me','Mẹ'),('con','Con')],"Quan hệ", required=True)

    @api.multi
    @api.onchange('age')  # if these fields are changed, call method
    def age_change(self):
        for rec in self:
            if rec.age:
                rec.birth_year = "%d"%(datetime.now().year - rec.age)
            else:
                rec.birth_year = "0"

    phone = fields.Char('Số ĐT')

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        result = super(FamilyMember, self).read(fields, load)
        for record in result:
            if 'birth_year' in record and 'age' in record:
                record['age'] = datetime.now().year - int(record['birth_year'])
        return result


# class Department(models.Model):
#     _name = 'hh.department'
#     name = fields.Char('Phòng')
#     parent_id = fields.Many2one('hh.department', string='Bộ phận cha', index=True)
#     child_ids = fields.One2many('hh.department', 'parent_id', string='Bộ phận con')
#     jobs_ids = fields.One2many('hh.job', 'department_id', string='Chức danh')
#
#     manager_id = fields.Many2one('hh.employee', string='Quản lý')
#     member_ids = fields.One2many('hh.employee', 'department_id', string='Members', readonly=True)

class Department(models.Model):
    _inherit = 'department'
    jobs_ids = fields.One2many('hh.job', 'department_id', string='Chức danh')