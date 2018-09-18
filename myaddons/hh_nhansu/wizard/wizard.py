# -*- coding: utf-8 -*-

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class ResignWizard(models.TransientModel):
    _name = "hh.employee.wizard"

    date_resign = fields.Date('Ngày nghỉ thực tế')
    date_confirm_resign = fields.Date('Ngày duyệt nghỉ')

    # @api.one
    def confirm_request(self):
        if 'active_id' in self._context:
            recs = self.env['hh.employee'].browse(self._context['active_id'])
            if recs.active:
                recs.date_resign = self.date_resign
                recs.date_confirm_resign = self.date_confirm_resign
                recs.active = False
            else:
                recs.active = True
