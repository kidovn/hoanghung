# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api

class KienDemo(models.Model):
    _name = 'kien.demo'
    _auto = False

    u_name = fields.Char(readonly=True)
    u_password = fields.Char(readonly=True)
    display_name = fields.Char(readonly=True)
    full_name = fields.Char(readonly=True)

    def _select_info(self):
        select_str = """
            ru.id,
            ru.login as u_name,
            ru.password as u_password,
            rp.display_name as display_name,
            CONCAT(ru.login, rp.display_name) as full_name
        """
        return select_str

    def _from(self):
        from_str = """
                res_users ru
                INNER JOIN res_partner rp ON ru.partner_id = rp.id
        """
        return from_str

    def _where(self):
        where_str = """
            1 = 1
        """

        return where_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'kien_demo')

        self._cr.execute("""
                        CREATE OR REPLACE VIEW kien_demo AS (
                    SELECT %s
                    FROM %s
                    WHERE %s
                    )""" % (
        self._select_info(), self._from(), self._where()))

