# -*- coding: utf-8 -*-
from odoo import models, fields, api
import functools

import logging
_logger = logging.getLogger(__name__)

date_field = [['date_pass','Ngày trúng tuyển']]

class Report(models.Model):
    _name = "hh.report"
    name = fields.Char('Tên báo cáo')
    model = fields.Char("Model")
    domain = fields.Char('domain')
    field_view = fields.Char('fields')



    @api.model
    def job_send_report(self, limit=None):
        _logger.info(limit)

    @api.model
    def fields_get_for_report(self, allfields=None, attributes=None):

        res = {}
        res['internclone'],res['invoice'] = self.env['intern.internclone'].fields_get_for_report(allfields,attributes)
        res['intern'] = self.env['intern.intern'].fields_get_for_report(allfields,attributes)
        data = {}
        data['fields'] = res
        data['date'] = date_field
        return data


class View(models.Model):
    _inherit = 'ir.ui.view'
    type = fields.Selection(selection_add = [('createreport',('CreateReport'))])


class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'
    view_mode = fields.Selection(selection_add = [('createreport',('CreateReport'))])

class ViewPivot(models.Model):
    _inherit = 'ir.ui.view'
    type = fields.Selection(selection_add = [('pivot_extend',('PivotExtend'))])


class ActWindowViewPivot(models.Model):
    _inherit = 'ir.actions.act_window.view'
    view_mode = fields.Selection(selection_add = [('pivot_extend',('PivotExtend'))])
