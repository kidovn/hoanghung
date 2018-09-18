# -*- coding: utf-8 -*-
from odoo import http, fields
from dateutil.relativedelta import relativedelta
import json
import logging
import urllib
import requests
import re
import datetime
from datetime import datetime
from werkzeug.utils import redirect
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)

class Website(http.Controller):
    @http.route('/task_manager', type='http', auth='public')
    def render_task_page(self, **kwargs):
        employees = request.env['hh.employee'].sudo().search([('room_type','=','8')])

        list_employee = []
        for employee in employees:
            if employee.job_id and u'TRƯỞNG PHÒNG' in employee.job_id.name.upper():
                continue
            list_employee.append(employee)

        jobs = request.env['employee.recruitment.job'].sudo().search([('active','=',True)])

        week_start = datetime.now() - relativedelta(days=datetime.now().weekday()%7)

        content = []
        for job in jobs:
            employee_jobs = []

            for employee in list_employee:
                task = request.env['employee.recruitment.task'].sudo().search(
                    [('job_id', '=', job.id),('employee_id','=',employee.id), ('create_date', '>=', week_start.strftime('%Y-%m-%d')),
                     ('create_date', '<=', (week_start + relativedelta(days=7)).strftime('%Y-%m-%d'))],limit=1)
                if task:
                    employee_jobs.append(task)
                else:
                    employee_jobs.append(None)
            content.append(employee_jobs)


        #
        #
        # invoices = sorted(invoices, key=lambda r: (tryconvert(r.date_exam_short),r.id))
        # form_tc = []
        # form_ct = []
        # for invoice in invoices:
        #     form_tc.append(len([intern for intern in invoice.interns_clone if intern.promoted == True]))
        #     form_ct.append(len([intern for intern in invoice.interns_clone if intern.confirm_exam == True]))

        return http.request.render('hh_sheet.employee_task_manager', {'employees':list_employee,'jobs':jobs,'content':content})

    @http.route('/push_task',type="http", auth='public', csrf=False)
    def push_task(self,**kwargs):
        _logger.info(kwargs)
        tasks = json.loads(kwargs['data'])
        for key in tasks:
            task = tasks[key]
            _logger.info("TASK %s"%task)
            target = 0
            achieve = 0
            if task['target'] != '':
                target = int(task['target'])
            if task['achieve'] != '':
                achieve = int(task['achieve'])

            if key.isdigit():
                _logger.info("KEY %s" % key)
                vals = {}
                vals['target'] = target
                vals['achieve'] = achieve

                task_load = request.env['employee.recruitment.task'].sudo().browse(int(key))
                task_load.write(vals)
            else:
                _logger.info("KEY11 %s" % key)
                job_id = int(task['job_id'])
                employee_id = int(task['employee_id'])
                vals = {}
                vals['target'] = target
                vals['achieve'] = achieve
                vals['job_id'] = job_id
                vals['employee_id'] = employee_id
                request.env['employee.recruitment.task'].sudo().create(vals)
        return