# -*- coding: utf-8 -*-
from odoo import models, fields, api

class InvoiceNew(models.Model):
    _inherit = 'intern.invoice'

    count_pass = fields.Integer(store=False,compute='_compute_pass')

    @api.multi
    def _compute_pass(self):
        for rec in self:
            if rec.interns_pass_doc:
                rec.count_pass = len(rec.interns_pass_doc)
            else:
                rec.count_pass = 0

