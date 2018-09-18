# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
from odoo.http import request

_logger = logging.getLogger(__name__)

class Province(models.Model):
    _inherit = 'province'
    name_in_jp = fields.Char('Tên tiếng Nhật')
    id_map = fields.Char('id_map')
    x_point = fields.Integer('X')
    y_point = fields.Integer('Y')
    column = fields.Integer('col')
    sort = fields.Integer('sort')



class Invoice(models.Model):
    _inherit = 'intern.invoice'

    @api.multi
    def print_maps(self):
        # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # _logger.info(request.httprequest.environ['HTTP_ORIGIN'])
        base_url = request.httprequest.environ['HTTP_ORIGIN']
        return {
            'type': 'ir.actions.act_url',
            'url': '%s/hh_maps/static/src/index.html?id=%d'%(base_url,self.id),
            'target': 'new',
        }

