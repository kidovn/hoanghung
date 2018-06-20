# -*- coding: utf-8 -*-

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class CancelInvoiceWizard(models.TransientModel):
    _name = "invoice.cancel.wizard"

    reason = fields.Char('Lý do')

    @api.multi
    def confirm_request(self):
        if 'action' in self._context and 'active_ids' in self._context:
            recs = self.env['active_model'].browse(self._context['active_ids'])
            if self._context['action'] == 'pause':
                for rec in recs:
                    rec.pause_invoice(self.reason)
            elif self._context['action'] == 'cancel':
                for rec in recs:
                    rec.cancel_invoice()
        return True