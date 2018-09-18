# -*- coding: utf-8 -*-

from odoo import models, fields, api, conf
import logging
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
import re
import xlsxwriter

import imp

fp, pathname, description = imp.find_module('tk_google_sheet',conf.addons_paths)
tk_google_sheet_module = imp.load_module('tk_google_sheet', fp, pathname, description)


_logger = logging.getLogger(__name__)

class ManageSheet(models.TransientModel):
    _name = "employee.sheet.wizard"

    # @api.model
    # def create(self, values):


    # # @api.one
    # def confirm_request(self):
    #     if 'active_id' in self._context:
    #         recs = self.env['hh.employee'].browse(self._context['active_id'])
    #         if recs.active:
    #             recs.date_resign = self.date_resign
    #             recs.date_confirm_resign = self.date_confirm_resign
    #             recs.active = False
    #         else:
    #             recs.active = True

    def send_data(self):
        spread_id = None
        sheet_name = None
        start_col = None
        end_col = None
        start_row = None
        if not sheet_name:
            sheet_name = 'Sheet1'

        if not spread_id:
            spread_id = '1NOVvwzyPHKItQJjlqJvfZnzv6GYH00AomehcSlhsacY'

        if not start_col:
            start_col = 'A'

        if not end_col:
            end_col = 'S'

        if not start_row:
            start_row = 4

        # sheet_content = self.build_content_for_employee_task()
        # _logger.info(len(sheet_content))
        service = tk_google_sheet_module.models.GoogleSheetWithVerifyCode().get_google_sheet_service_object()
        start_col = xlsxwriter.utility.xl_col_to_name(5)
        start_row = 1
        employee_content = []
        employees = self.env['hh.employee'].search([('room_type','=','8')])
        counter = 0
        for employee in employees:
            if employee.job_id and u'TRƯỞNG PHÒNG' in employee.job_id.name.upper():
                continue
            employee_content.append(employee.id)
            employee_content.append(employee.name)
            counter+=1

        end_col = xlsxwriter.utility.xl_col_to_name(5 + counter*2)

        range_name = sheet_name + '!' + str(start_col) + str(start_row) + ':' + str(end_col) + str(1)
        service.spreadsheets().values().update(
                    spreadsheetId=spread_id, range=range_name,
                    valueInputOption="RAW", body={'values': [employee_content]}).execute()

        requests = [{
              "updateBorders": {
                "range": {
                  "sheetId": 0,
                  "startRowIndex": 0,
                  "endRowIndex": 10,
                  "startColumnIndex": 0,
                  "endColumnIndex": 6
                },
                "top": {
                  "style": "DASHED",
                  "width": 1,
                  "color": {
                    "blue": 1.0
                  },
                },
                "bottom": {
                  "style": "DASHED",
                  "width": 1,
                  "color": {
                    "blue": 1.0
                  },
                },
                "innerHorizontal": {
                  "style": "DASHED",
                  "width": 1,
                  "color": {
                    "blue": 1.0
                  },
                },
              }
            }]
        request = service.spreadsheets().batchUpdate(spreadsheetId=spread_id, body={'requests':requests})
        response = request.execute()

        if 'error' in response:
            _logger.info("Google spreadsheet create new sheet failed, spread_id: %s, error: %s" % (
                spread_id, response['error']))


    @api.model
    def build_content_for_employee_task(self):
        sheet_content = []

        list_receivables = self.env['employee.recruitment.task'].search([])
        for rec in list_receivables:
            sheet_content.append([rec.job_id.name,
                                  rec.employee_id.name if rec.employee_id else '',
                                  rec.target
                                  ])

        return sheet_content