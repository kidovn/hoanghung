# -*- coding: utf-8 -*-

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class CancelInvoiceWizard(models.TransientModel):
    _name = "invoice.cancel.wizard"

    start_date = fields.Date('Từ ngày')
    end_date = fields.Date('Đến ngày')

    @api.multi
    def confirm_request(self):
        
        return True