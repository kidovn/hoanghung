# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
import re
_logger = logging.getLogger(__name__)



class Candidate(models.Model):
    _name = 'hh.candidate'
    _order = 'id desc'
    _sql_constraints = [('email_unique', 'UNIQUE(email)', 'email đã tồn tại trong hệ thống'),
                        ('phone_unique', 'UNIQUE(phone_number)', 'phone_number đã tồn tại trong hệ thống'),
                        ('contact_info_null','CHECK (COALESCE(phone_number, email, facebook, address) IS NOT NULL)','Cần ít nhất một phương thức liên lạc với người này')]
    name = fields.Char('Họ tên',required =True )
    name_without_signal = fields.Char('Họ tên ko dấu')
    birth_day = fields.Char('Ngày sinh')
    birth_month = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")
    birth_year = fields.Char('Năm sinh')

    gender = fields.Selection([('nam', 'Nam'), ('nu', 'Nữ')], string='Giới tính')

    phone_number = fields.Char("Số điện thoại")

    email = fields.Char('Email')

    facebook = fields.Char('Facebook')

    province = fields.Many2one("province",string="Quê quán")

    address = fields.Char('Địa chỉ liên lạc')

    school_name = fields.Char('Tên trường')

    foreign_language = fields.Char('Trình độ NN')

    experience = fields.Char('Kinh nghiệm')

    aspiration = fields.Char('Nguyện vọng')

    position_apply = fields.Char('Vị trí ứng tuyển')

    date_apply = fields.Date('Ngày ứng tuyển')

    date_interview = fields.Date('Ngày phỏng vấn')

    @api.model
    def _default_employee_care(self):
        resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)], limit=1)
        if resource:
            return self.env['hh.employee'].search([('resource_id','=',resource.id)], limit=1)
        else:
            return False

    employee_care = fields.Many2one('hh.employee',string=u"Nhân viên care",default =_default_employee_care)

    interviewers = fields.Char('TP tham gia pv')

    result = fields.Selection([('1','Đạt'),('2','Không đạt')],string='Kết quả')

    # note = fields.Char('Ghi chú')

    date_start_working = fields.Date('Ngày đi làm')

    date_notice_user = fields.Date('Ngày cảnh báo đi làm',store=True,compute='compute_date_notice')

    schedule_call_back = fields.Datetime('Lập lịch liên hệ lại')

    event = fields.Many2one('hh.event','Lập lịch liên hệ lại')

    notes = fields.One2many('hh.candidate.note','candidate_id',string='Ghi chú')

    current_job = fields.Selection([('1','Quản lý TTS'),('2','Phiên dịch ngắn hạn'),('3','PTTT công ty khác bên Nhật'),
                                    ('4','PTTT công ty khác tại Việt Nam'),('5','Khác')],string='Công việc hiện tại',required=True)
    current_job_other = fields.Char('Chi tiết công việc khác')

    cooperate_type = fields.Selection([('1','Là ứng viên'),('2','Cộng tác đưa đơn hàng'),('3','Cộng tác đưa lao động')],string='Tiềm năng cộng tác',default='1',required=True)
    # @api.multi
    # @api.onchange('result')
    # def onchange_result(self):
    #     for rec in self:
    #         if rec.result and rec.result == '2':
    #             rec.date_start_working = False

    @api.model
    def create(self, vals):
        if 'phone_number' not in vals and 'email' not in vals and 'facebook' not in vals:
            raise ValidationError(u'Cần ít nhất một phương thức liên lạc với người này')
        if 'phone_number' in vals and vals['phone_number']:
            vals['phone_number'] = re.sub(r"\s", "", vals['phone_number'])
        record = super(Candidate,self).create(vals)
        if 'schedule_call_back' in vals:
            if vals['schedule_call_back']:
                tmp = {}
                tmp['name'] = u'Bạn có ứng viên cần liên hệ lại'
                alarm = self.env['hh.alarm'].search([('type','=','notification'),('interval','=','minutes'),('duration','=',10)])
                if not alarm:
                    tmp_alarm = {}
                    tmp_alarm['type'] = 'notification'
                    tmp_alarm['interval'] = 'minutes'
                    tmp_alarm['duration'] = 10
                    tmp_alarm['name'] = '10 minutes'
                    alarm = self.env['hh.alarm'].create(tmp_alarm)

                tmp['alarm_ids'] = [(6,0,[alarm.id])]
                tmp['start'] = vals['schedule_call_back']
                tmp['start_datetime'] = vals['schedule_call_back']
                tmp['stop'] = vals['schedule_call_back']
                tmp['stop_datetime'] = vals['schedule_call_back']
                if 'position_apply' in vals and vals['position_apply']:
                    tmp['description'] = u'%s ứng tuyển vị trí %s'%(vals['name'],vals['position_apply'])
                else:
                    tmp['description'] = vals['name']
                tmp['action'] = 'hh_schedule_notification.action_hh_event_notify'
                event = self.env['hh.event'].create(tmp)
                record.event = event.id
                record.write({'event':event.id})
        return record

    @api.multi
    def write(self, vals):
        record = super(Candidate, self).write(vals)
        if 'schedule_call_back' in vals:
            if vals['schedule_call_back']:
                if self.event:
                    self.event.unlink()
                tmp = {}
                tmp['name'] = u'Bạn có ứng viên cần liên hệ lại'
                alarm = self.env['hh.alarm'].search(
                    [('type', '=', 'notification'), ('interval', '=', 'minutes'), ('duration', '=', 10)])
                if not alarm:
                    tmp_alarm = {}
                    tmp_alarm['type'] = 'notification'
                    tmp_alarm['interval'] = 'minutes'
                    tmp_alarm['duration'] = 10
                    tmp_alarm['name'] = '10 minutes'
                    alarm = self.env['hh.alarm'].create(tmp_alarm)

                tmp['alarm_ids'] = [(6, 0, [alarm.id])]
                tmp['start'] = vals['schedule_call_back']
                tmp['start_datetime'] = vals['schedule_call_back']
                tmp['stop'] = vals['schedule_call_back']
                tmp['stop_datetime'] = vals['schedule_call_back']
                if self.position_apply or 'position_apply' in vals:
                    if 'name' in vals:
                        name = vals['name']
                    else:
                        name = self.name
                    if 'position_apply' in vals:
                        position_apply = vals['position_apply']
                    else:
                        position_apply = self.position_apply
                    tmp['description'] = u'%s ứng tuyển vị trí %s' % (name, position_apply)
                else:
                    tmp['description'] = self.name
                tmp['action'] = 'hh_schedule_notification.action_hh_event_notify'
                event = self.env['hh.event'].create(tmp)
                self.event = event.id
                self.write({'event': event.id})
            else:
                if self.event:
                    self.event.unlink()
        return record


    @api.multi
    def unlink(self):
        for id in self.ids:
            self._cr.execute('SELECT create_uid, name FROM hh_candidate WHERE hh_candidate.id = %s'%id)
            tmpresult = self._cr.fetchone()
            if tmpresult[0] != self.env.uid:
                raise ValidationError(u"Bạn không có quyền xoá ứng viên %s"%tmpresult[1])
        super(Candidate,self).unlink()

    @api.multi
    @api.depends('date_start_working')
    def compute_date_notice(self):
        for rec in self:
            if rec.date_start_working:
                tmpdate = datetime.strptime(rec.date_start_working,'%Y-%m-%d') - timedelta(days=1)
                if tmpdate.weekday() == 6:
                    rec.date_notice_user = tmpdate - timedelta(days=1)
                else:
                    rec.date_notice_user = tmpdate
            else:
                rec.date_notice_user = False

    care = fields.Boolean('Có quan tâm')
    fbpage_id = fields.Many2one('candidate.facebook',string='Thuộc trang fb')
    people_suggest_id = fields.Many2one('hh.candidate',string='Người giới thiệu')
    people_care = fields.One2many('hh.candidate','people_suggest_id',string='Người quan tâm')

    #Thong tin neu la thuc tap sinh
    is_intern = fields.Boolean('Là thực tập sinh')
    intern_job = fields.Char('Ngành nghề')
    intern_work_place = fields.Many2one('japan.province','Tỉnh làm việc')
    intern_salary = fields.Char("Lương thực lĩnh")
    intern_dispatchcom = fields.Many2one('hh.candidate.dispatch','Công ty phái cử')
    intern_month_start = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                     ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                     ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng bắt đầu",required=True)

    intern_year_start = fields.Char("Năm bắt đầu", size=4,required=True)

    intern_month_end = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                           ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                           ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng về nước",
                                          required=True)

    intern_year_end = fields.Char("Năm về nước", size=4, required=True)
    intern_family_number = fields.Char('Số điện thoại gia đình')
    intern_accept_col_resource = fields.Boolean('TTS đồng ý làm ctv nguồn')
    intern_family_accept_col_resource = fields.Boolean('Gia đình TTS đồng ý làm ctv nguồn')
    intern_note = fields.Char('Lưu ý khác')


class Note(models.Model):
    _name = 'hh.candidate.note'
    name = fields.Char('Nội dung')
    candidate_id = fields.Many2one('hh.candidate',string='Ứng viên')

    @api.one
    def write(self, vals):
        raise ValidationError('Bạn ko cần phải sửa ghi chú. Tạo mới ghi chú khác nếu muốn')
# class CandidateJob(models.Model):
#     _name = 'hh.candidate.job'
#     name = fields.Char('Công việc')

class DispatchCom(models.Model):
    _name = 'hh.candidate.dispatch'
    name = fields.Char('Tên cty phái cử')

