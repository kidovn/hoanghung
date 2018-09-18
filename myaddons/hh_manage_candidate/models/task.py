# -*- coding: utf-8 -*-

from odoo import models, fields, api, conf
import logging
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
import re

import imp

fp, pathname, description = imp.find_module('tk_google_sheet',conf.addons_paths)
tk_google_sheet_module = imp.load_module('tk_google_sheet', fp, pathname, description)


_logger = logging.getLogger(__name__)


class Job(models.Model):
    _name = 'employee.recruitment.job'
    active = fields.Boolean('Active', default=True)
    name = fields.Char('Vị trí tuyển dụng')
    # kind = fields.Selection([('1','Ngắn hạn'),('2','Dài hạn')], required=True,string='Ngắn/Dài hạn')

class Task(models.Model):
    _name = 'employee.recruitment.task'
    job_id = fields.Many2one('employee.recruitment.job', string='Vị trí TD')
    # employee = fields.
    employee_id = fields.Many2one('hh.employee', string='Nhân viên tuyển dụng', domain=[('room_type','=','8')])
    date_start = fields.Date('Từ ngày', default=lambda self: self._get_default_date_start())
    date_end = fields.Date('Đến ngày', default=lambda self: self._get_default_date_end())
    target = fields.Integer('Chỉ tiêu')
    achieve = fields.Integer('Hoàn thành')

    @api.model
    def _get_default_date_start(self):
        return datetime.today() - timedelta(days=datetime.today().isoweekday() % 7+1)

    @api.model
    def _get_default_date_end(self):
        return datetime.today() - timedelta(days=datetime.today().isoweekday() % 7) + timedelta(days=7)


    @api.multi
    def job_show_receivable_employee_to_google_sheet(self):
        """
        push sheet content to google spreadsheet
        :param spread_id:
        :param sheet_name:
        :return:
        """
        spread_id = None
        sheet_name = None
        start_col = None
        end_col = None
        start_row = None
        if not sheet_name:
            sheet_name = 'Employees'

        if not spread_id:
            spread_id = '1pIbUl2rnrS31OBDJAGofdbgsB9MwPzQYA7aGWTdiLZE'

        if not start_col:
            start_col = 'A'

        if not end_col:
            end_col = 'S'

        if not start_row:
            start_row = 4

        sheet_content = self.build_content_for_employee()
        _logger.info(len(sheet_content))
        tk_google_sheet_module.models.GoogleSheetWithVerifyCode().send(spread_id, sheet_name, sheet_content, start_col,
                                                                       end_col, start_row)

    @api.model
    def build_content_for_employee(self):
        sheet_content = []

        list_receivables = self.env['employee.recruitment.task'].search([])
        for rec in list_receivables:
            sheet_content.append([rec.job_id.name,
                                  rec.employee_id.name if rec.employee_id else '',
                                  rec.target
                                  ])

        return sheet_content


class Employee(models.Model):
    _inherit = 'hh.employee'

    tasks = fields.One2many('employee.recruitment.task','employee_id')