# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime

class Website(http.Controller):
    @http.route('/don_hang', type='http', auth='public', website=True)
    def render_invoices_page(self, **kwargs):
        invoices = request.env['intern.invoice'].sudo().search([('status','!=',2),('status','!=',3),('status','!=',6),('status','!=',7),('hoso_created','!=',True)])

        def tryconvert(date_str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except (ValueError,TypeError):
                return datetime(1, 1, 1)

        invoices = sorted(invoices, key=lambda r: (tryconvert(r.date_exam_short),r.id))
        form_tc = []
        form_ct = []
        for invoice in invoices:
            form_tc.append(len([intern for intern in invoice.interns_clone if intern.promoted == True]))
            form_ct.append(len([intern for intern in invoice.interns_clone if intern.confirm_exam == True]))

        return http.request.render('hh_website.invoices_page', {'invoices':invoices,'form_tc':form_tc,'form_ct':form_ct})



    @http.route('/invoice/<invoice_id>',type='http', auth='public', website=True)
    def render_invoice_detail(self,invoice_id, **kwargs):
        invoice = request.env['intern.invoice'].sudo().browse(int(invoice_id))
        interns = sorted(invoice.interns_clone, key =lambda x: x.condition_count2,reverse=True)
        return http.request.render('hh_website.invoices_detail', {'invoice':invoice,'interns':interns})