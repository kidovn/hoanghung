# -*- coding: utf-8 -*

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class Employee(models.Model):
    _name = 'hh.employee'
    _description = u'Nhân viên'
    name= fields.Char("Tên", required=True)
    gender = fields.Selection([('nam', 'Nam'), ('nu', 'Nữ')])



    #ngay sinh
    day = fields.Char("Ngày", size=2)
    month = fields.Selection([(1, '01'), (2, '02'), (3, '03'), (4, '04'),
                              (5, '05'), (6, '06'), (7, '07'), (8, '08'),
                              (9, '09'), (10, '10'), (11, '11'), (12, '12'), ], "Tháng")

    year = fields.Char("Năm", size=4)

    date_of_birth = fields.Char("Ngày sinh", store=False, compute='_date_of_birth')

    @api.one
    @api.depends('day', 'month', 'year')
    def _date_of_birth(self):
        self.date_of_birth = "%s/%s/%s" % (self.day, self.month, self.year)

    room_type = fields.Selection(
        [('0', 'Tuyển dụng'), ('1', 'Phát triển thị trường'), ('2', 'Kiểm soát'), ('3', 'Đối ngoại'),
         ('4', 'Hồ sơ'), ('5', 'Kế toán')], string="Phòng ban")

class Department(models.Model):
    _name = 'department'
    _description = u'Phòng ban'
    room_type = fields.Selection([('0','Tuyển dụng'),('1','Phát triển thị trường'),('2','Kiểm soát'),('3','Đối ngoại'),
                                  ('4','Hồ sơ'),('5','Kế toán')],string="Phòng", required=True)
    name = fields.Char("Tên")
    manager = fields.Many2one('hh.employee',string="Trưởng phòng")
    members = fields.Many2many('hh.employee')

    @api.onchange('room_type')
    def domain_for_member(self):
        if self.room_type:
            return {'domain': {'members': [('room_type', '=', self.room_type)]}}

    @api.onchange('room_type')
    def domain_for_manager(self):
        if self.room_type:
            return {'domain': {'manager': [('room_type', '=', self.room_type)]}}

