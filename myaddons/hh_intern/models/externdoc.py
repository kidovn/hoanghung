# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ExternDocument(models.Model):
    _name = 'intern.externdoc'
    _description = u'Hồ sơ ngoại'
    intern = fields.Many2one('intern.intern')
    dispatchcom2 = fields.Many2one('dispatchcom2')
    dispatchcom1 = fields.Many2one('dispatchcom1')
    training_center = fields.Many2one('trainingcenter')
    guild = fields.Many2one('intern.guild')
    enterprise = fields.Many2one('intern.enterprise')