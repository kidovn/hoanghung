# -*- coding: utf-8 -*

from odoo import models, fields, api
import logging
from odoo import tools, _
from odoo.modules.module import get_module_resource
_logger = logging.getLogger(__name__)

class Employee(models.Model):
    _name = 'hh.employee'
    _description = u'Nhân viên'

    _inherits = {'resource.resource': "resource_id"}

    name_related = fields.Char(related='resource_id.name', string="Resource Name", readonly=True, store=True)

    #
    # resource_id = fields.Many2one('resource.resource', string='Resource',
    #                               ondelete='cascade', required=True, auto_join=True)

    gender = fields.Selection([('nam', 'Nam'), ('nu', 'Nữ')],string='Giới tính')

    @api.model
    def _default_image(self):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    image = fields.Binary("Photo", default=_default_image, attachment=True,
                          help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo", attachment=True,
                                 help="Medium-sized photo of the employee. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved. "
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized photo", attachment=True,
                                help="Small-sized photo of the employee. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(Employee, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(Employee, self).write(vals)

    @api.onchange('user_id')
    def _onchange_user(self):
        self.name = self.user_id.name

    date_of_birth = fields.Date("Ngày sinh")

    room_type = fields.Selection(
        [('0', 'Tuyển dụng'), ('1', 'Phát triển thị trường'), ('2', 'Kiểm soát'), ('3', 'Đối ngoại'),
         ('4', 'Hồ sơ'), ('5', 'Kế toán'),('6','Hành chính NS'),('7','Đào tạo'),('8','Tuyển dụng NS')], string="Phòng ban")

    # department_hs = fields.Many2many('department',string='Phụ trách hồ sơ của các phòng')
    department_id = fields.Many2one('department', string="Phòng")

    @api.multi
    @api.depends('department_id')
    @api.onchange('department_id')
    def onchage_department_id(self):
        for rec in self:
            rec.room_type = rec.department_id.room_type


class Department(models.Model):
    _name = 'department'
    _description = u'Phòng ban'
    room_type = fields.Selection([('0','Tuyển dụng'),('1','Phát triển thị trường'),('2','Kiểm soát'),('3','Đối ngoại'),
                                  ('4','Hồ sơ'),('5','Kế toán'),('6','Hành chính NS'),('7','Đào tạo'),('8','Tuyển dụng NS')],string="Phòng", required=True)
    name = fields.Char("Tên phòng")
    manager = fields.Many2one('hh.employee',string="Trưởng phòng")
    members = fields.One2many('hh.employee','department_id', string='Members', readonly=True)

    # groups = fields.One2many("department.group", "department_id", string="Nhóm")
    #
    # block = fields.Many2one('department.block',string='Khối TD')

    @api.onchange('room_type')
    def domain_for_member(self):
        if self.room_type:
            return {'domain': {'members': [('room_type', '=', self.room_type)]}}

    @api.onchange('room_type')
    def domain_for_manager(self):
        if self.room_type:
            return {'domain': {'manager': [('room_type', '=', self.room_type)]}}

    # @api.model
    # def create(self, vals):
    #     if vals['room_type'] == '0':
    #         if 'members' in vals:
    #             vals['members'] = False
    #     else:
    #         if 'groups' in vals:
    #             vals['groups'] = False
    #
    #         if 'block' in vals:
    #             vals['block'] = False
    #     return super(Department, self).create(vals)

    @api.onchange('room_type')
    def onchange_place(self):
        res = {}
        if self.room_type:
            res['domain'] = {'manager': [('room_type', '=', self.room_type)],
                             'members': [('room_type', '=', self.room_type)]}
        return res


    parent_id = fields.Many2one('department', string='Bộ phận cha', index=True)
    child_ids = fields.One2many('department', 'parent_id', string='Bộ phận con')




class Group(models.Model):
    _name= 'department.group'
    _description = u'Nhóm tuyển dụng'

    name=fields.Char('Tên nhóm')

    department_id= fields.Many2one('department',string='Phòng TD', required=True)

    members = fields.Many2many('hh.employee')

class Block(models.Model):
    _name = 'department.block'
    _description = u'Khối tuyển dụng'

    name = fields.Char('Tên khối')


class TargetDeparment(models.Model):
    _name = 'intern.department'
    _inherits = {'department': 'intern_id'}
    department_id = fields.Many2one('department', required=True, ondelete='restrict', auto_join=True,
                                string='Phòng TD', help='PTTT-related data of the user')

    invoice_id = fields.Many2one("intern.invoice", string='Đơn hàng', ondelete='cascade')

    target_men = fields.Integer('Chỉ tiêu nam', default=0)
    target_women = fields.Integer('Chỉ tiêu nữ', default=0)

