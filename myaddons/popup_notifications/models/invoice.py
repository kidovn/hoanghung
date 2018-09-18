# -*- coding: utf-8 -*-
from odoo import models, fields, api

from tempfile import TemporaryFile, NamedTemporaryFile
from io import BytesIO
from datetime import datetime, date
from docxtpl import DocxTemplate, InlineImage, CheckedBox, CheckBox, RichText, Tick
from docx.shared import Mm, Inches
from docx import Document
import os
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class Invoice(models.Model):
    _inherit = 'intern.invoice'

    # @api.multi
    # def unlink(self):
    #     return super(Invoice, self).unlink()

    @api.one
    def start_promotion(self):
        ensure_one = False
        for intern in self.interns_clone:
            if intern.promoted:
                ensure_one = True
                break

        if ensure_one:
            self.write({
                'status': 5,
            })
            group_ids = self.env['ir.model.data'].search([('module','=','hh_intern'),('name','in',['group_user','group_manager','group_ks_user']),('model','=','res.groups')])
            if group_ids:
                list_group = []
                for group in group_ids:
                    list_group.append(group.res_id)
                doingoais = self.env['res.users'].search([('groups_id','in',list_group)])
                if doingoais:
                    values = {'status': 'draft', 'title': u'Thông báo tiến cử',
                              'message': u'Đơn hàng "%s" đã chốt danh sách tiến cử'%self.name,
                              'partner_ids': [(6, 0, doingoais.ids)]
                              }
                    self.env['popup.notification'].create(values)

        else:
            raise ValidationError(u"Chưa có TTS nào trong danh sách tiến cử")

    @api.one
    def confirm_exam(self):
        ensure_one = False
        for intern in self.interns_clone:
            if intern.confirm_exam and not intern.issues_raise:
                ensure_one = True
                break
        if ensure_one:
            self.write({
                'status': 1,
            })
            for intern in self.interns_clone:
                intern.write({
                    'exam': True,
                })

            group_ids = self.env['ir.model.data'].search(
                [('module', '=', 'hh_intern'), ('name', 'in', ['group_ks_user', 'group_manager']),
                 ('model', '=', 'res.groups')])
            if group_ids:
                list_group = []
                for group in group_ids:
                    list_group.append(group.res_id)
                doingoais = self.env['res.users'].search([('groups_id', 'in', list_group)])
                if doingoais:
                    values = {'status': 'draft', 'title': u'Thông báo thi tuyển',
                              'message': u'Đơn hàng "%s" đã chốt danh sách thi tuyển' % self.name,
                              'partner_ids': [(6, 0, doingoais.ids)]
                              }
                    self.env['popup.notification'].create(values)

        else:
            raise ValidationError(u"Chưa có TTS nào trong danh sách chốt thi tuyển")

    @api.one
    def confirm_pass(self):
        ensure_one = False
        for intern in self.interns_clone:
            if intern.pass_exam and not intern.issues_raise:
                ensure_one = True
                break
        if ensure_one:
            self.write({
                'status': 2,
            })
            for intern in self.interns_clone:
                intern.write({
                    'done_exam': True,
                })

            group_ids = self.env['ir.model.data'].search(
                [('module', '=', 'hh_intern'), ('name', 'in', ['group_ks_user', 'group_manager','group_hs_user','group_hs_manager']),
                 ('model', '=', 'res.groups')])
            if group_ids:
                list_group = []
                for group in group_ids:
                    list_group.append(group.res_id)
                doingoais = self.env['res.users'].search([('groups_id', 'in', list_group)])
                if doingoais:
                    values = {'status': 'draft', 'title': u'Thông báo trúng tuyển',
                              'message': u'Đơn hàng "%s" đã chốt danh sách trúng tuyển' % self.name,
                              'partner_ids': [(6, 0, doingoais.ids)]
                              }
                    self.env['popup.notification'].create(values)
        else:
            raise ValidationError(u"Chưa có TTS nào trong danh sách trúng tuyển")