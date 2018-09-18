# -*- coding: utf-8 -*-

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class DepositWizard(models.TransientModel):
    _name = "intern.accounting.deposit.wizard"

    employee_deposit = fields.Many2one('hh.employee', string='Cán bộ nộp cọc')
    # employee_withdraw = fields.Many2one('hh.employee', string='Cán bộ rút cọc')
    money_deposit = fields.Integer('Tiền cọc', default=10000000)

    # @api.one
    def confirm_request(self):
        if 'active_id' in self._context:
            recs = self.env['intern.intern'].browse(self._context['active_id'])
            # recs.employee_deposit = self.employee_deposit
            # recs.money_deposit = self.money_deposit
            # recs.have_deposit = True
            recs.write({'employee_deposit':self.employee_deposit.id,'money_deposit':self.money_deposit,'have_deposit':True})


class WithdrawWizard(models.TransientModel):
    _name = "intern.accounting.withdraw.wizard"

    # employee_deposit = fields.Many2one('hh.employee', string='Cán bộ nộp cọc')
    employee_withdraw = fields.Many2one('hh.employee', string='Cán bộ rút cọc')
    # money_deposit = fields.Integer('Tiền cọc', default=10000000)

    # @api.one
    def confirm_request(self):
        if 'active_id' in self._context:
            recs = self.env['intern.intern'].browse(self._context['active_id'])
            # recs.employee_withdraw = self.employee_withdraw
            # recs.money_deposit = 0
            # recs.have_deposit = False
            # recs.write({})
            recs.write({'employee_withdraw': self.employee_withdraw.id, 'money_deposit': 0,
                        'have_deposit': False})