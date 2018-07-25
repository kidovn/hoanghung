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

class PrintDocWizard(models.TransientModel):
    _name = "invoice.printdoc.wizard"
    document = fields.Selection([('Doc1-3', '1-3'), ('Doc1-10', '1-10'), ('Doc1-13', '1-13'), ('Doc1-20', '1-20'),
                                 ('Doc1-21', '1-21'), ('Doc1-28', '1-28'), ('Doc1-29', '1-29'),
                                 ('DocCCDT', 'Chứng chỉ kết thúc Đào tạo'),
                                 ('HDPC', 'Hợp đồng PC'), ('PROLETTER', 'Thư tiến cử'),('DSLD','Danh sách lao động')
                                    ,('CheckList','Check List')], string='Hồ sơ in')

    enterprise = fields.Many2one('intern.enterprise',string='Xí nghiệp',required=True)

    # @api.multi
    def _get_enterprise_domain(self):
        education_list = []
        invoice_id = self._context['active_id']
        invoice = self.env['intern.invoice'].browse(invoice_id)
        for x in invoice.interns_pass_doc:
            if x.enterprise:
                education_list.append(x.enterprise.id)
        return [(6, 0, education_list)]

    enterprise_ids = fields.Many2many('intern.enterprise',default=_get_enterprise_domain)

    def confirm_request(self):
        _logger.info("confirm")
        invoice_id = self._context['active_id']
        invoice = self.env['intern.invoice'].browse(invoice_id)
        return invoice.create_extern_doc(self.enterprise.id,self.document)



class PrintFormCustomWizard(models.TransientModel):
    _name = "invoice.printform.wizard"

    # @api.multi
    def _get_interns_domain(self):
        education_list = []
        invoice_id = self._context['active_id']
        invoice = self.env['intern.invoice'].browse(invoice_id)
        for x in invoice.interns_exam_doc:
            education_list.append(x.id)
        return [(6, 0, education_list)]

    interns_list = fields.Many2many('intern.internclone', default=_get_interns_domain)
    interns = fields.Many2many('intern.internclone')


