# -*- coding: utf-8 -*-

from odoo import api, fields, models


class InternWizard(models.TransientModel):
    _name = "intern.wizard"

    salesperson_id = fields.Many2one('res.users', string='Salesperson', required=True)