# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime
from odoo.exceptions import ValidationError
import intern_utils
import province
_logger = logging.getLogger(__name__)

class InternOrder(models.Model):
    _name='intern.order'

    invoice_id = fields.Integer(string='InvoiceId')
    intern_id = fields.Integer(string='InternId')

