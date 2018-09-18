# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class Intern(models.Model):
    _inherit = 'intern.intern'


    # @api.multi
    # def toggle_deposit(self):
    #     for rec in self:
    #         rec.write({'have_deposit': not rec.have_deposit})


    employee_deposit = fields.Many2one('hh.employee',string='Cán bộ nộp cọc')
    employee_withdraw = fields.Many2one('hh.employee',string='Cán bộ rút cọc')
    money_deposit = fields.Integer('Tiền cọc')

    @api.one
    def write(self, vals):
        old_deposit = self.money_deposit
        super(Intern,self).write(vals)
        if 'have_deposit' in vals:
            logdeposit = {'intern_id' : self.id}
            logdeposit.update({'have_deposit':vals['have_deposit']})
            if 'employee_deposit' in vals:
                logdeposit.update({'employee_deposit': vals['employee_deposit']})
                if 'money_deposit' in vals:
                    logdeposit.update({'money_deposit': vals['money_deposit']})
            if 'employee_withdraw' in vals:
                logdeposit.update({'employee_withdraw': vals['employee_withdraw'],'money_deposit':old_deposit})



            log = self.env['intern.deposit.history'].create(logdeposit)
            # log.intern_id = [(4, intern.id)]



class LogDeposit(models.Model):
    _name = 'intern.deposit.history'
    intern_id = fields.Many2one('intern.intern',string='TTS')
    have_deposit = fields.Boolean(string="Đặt cọc")
    employee_deposit = fields.Many2one('hh.employee', string='Cán bộ nộp cọc')
    employee_withdraw = fields.Many2one('hh.employee', string='Cán bộ rút cọc')
    money_deposit = fields.Integer('Tiền cọc')