# -*- coding: utf-8 -*-

from odoo import models, fields, api

import os
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import xlwt
import json
import ast
import base64
from io import BytesIO, StringIO
import logging
import re
from datetime import datetime
import sys
_logger = logging.getLogger(__name__)

class IrCron(models.Model):
    _name='hh.cron'
    _inherits = {'ir.cron': 'cron_job_id'}
    # name = fields.Char('Tên báo cáo')
    cron_job_id = fields.Many2one('ir.cron', string='Cron job', auto_join=True,  ondelete="cascade", required=True)


    body_content = fields.Text('Nội dung email')

    emails = fields.Char('Địa chỉ email nhận')

    report = fields.Many2one('ir.filters',string='Loại báo cáo',
                             domain="[('active','=',True),'|','|','|',('model_id','=','intern.report'),('model_id','=','intern.internclone')"
                                    ",('model_id','=','intern.intern'),('model_id','=','intern.invoice')]")


    @api.model
    def create(self, vals):
        vals['function'] = 'excute_send_mail'
        vals['model'] = 'hh.cron'
        vals['args'] = False
        vals['doall'] = True
        vals['numbercall'] = -1
        res = super(IrCron, self).create(vals)
        res.args = res._ids
        return res
    #     valcron = {}
    #     valcron['interval_number'] = vals['interval_number']
    #     valcron['interval_type'] = vals['interval_type']
    #     valcron['nextcall'] = vals['date_start']
    #     valcron['model'] = 'hh.cron'
    #     valcron['function'] = 'excute_send_mail'
    #     valcron['args'] = res.id
    #     self.env['ir.cron'].create(valcron)
    #     return res

    @api.model
    def excute_send_mail(self,id):
        self = self.with_context(lang=u'vi_VN')
        cron = self.env['hh.cron'].browse(id)
        if cron:
            cron.method_direct_trigger()


    def method_direct_trigger(self):
        # reload(sys)
        # sys.setdefaultencoding('utf-8')
        if not self._context:
            self._context = {'lang': u'vi_VN'}
        if self.report:
            _logger.info("DO NOTHING %s"%self.report.context.replace("u\\'",'"').replace("'",'"').replace('u"','"'))
            context = json.loads(self.report.context.replace("u\\'",'"').replace("'",'"').replace('u"','"'))

            active_measures = None
            if 'measures' in context:
                active_measures = context['measures']
            elif 'pivot_measures' in context:
                active_measures = context['pivot_measures']
            if active_measures!= None:
                fields_model = self.env[self.report.model_id].fields_get()
                groupby = None
                if 'group_by' in context:
                    groupby = context['group_by']
                elif 'pivot_row_groupby' in context:
                    groupby = context['pivot_row_groupby']
                col_groupby = None
                if 'col_group_by' in context:
                    col_groupby = context['col_group_by']
                elif 'pivot_column_groupby' in context:
                    col_groupby = context['pivot_column_groupby']

                fields = list(active_measures)
                if groupby is not None:
                    fields.extend(x.split(':')[0] for x in groupby if x not in fields)
                if col_groupby is not None:
                    fields.extend(x.split(':')[0] for x in col_groupby if x not in fields)
                datas = []
                tmp_groupbys = []
                tmp_domain = self.report.domain
                if 'time.str' in tmp_domain:
                    times = re.findall(r'time.strftime\("[%,\-,\w]*"\)',tmp_domain)
                    for time in times:
                        tmp = time.replace('time.strftime(','').replace('%Y','%d'%datetime.now().year)\
                                        .replace('%m','%d'%datetime.now().month).replace(")",'')
                        tmp_domain = tmp_domain.replace(time,tmp)

                domains = ast.literal_eval(tmp_domain)
                # for domain in domains:
                #     if type(domain) is str:
                #
                datas.append(self.env[self.report.model_id].read_group(domains, fields, tmp_groupbys,lazy=False))
                for group in groupby:
                    tmp_groupbys.append(group)
                    datas.append(self.env[self.report.model_id].read_group(domains,fields,tmp_groupbys,lazy=False))

                workbook = xlwt.Workbook()
                worksheet = workbook.add_sheet(self.report.name)

                header_plain = xlwt.easyxf("pattern: pattern solid, fore_colour gray25;")
                for i, header_row in enumerate(active_measures):
                    worksheet.write(0, i + 1, u'%s'%(fields_model[header_row]['string']),header_plain)

                # row_counter = 1
                # worksheet.write(row_counter,0,'Tổng')
                # for i in
                # for i,header_row in enumerate(active_measures):
                #     worksheet.write(1, i+1, 'Tổng')

                self.write_table(worksheet,datas,1,0,active_measures,groupby)
                # workbook.save("trial.xls")
                byteIo = BytesIO()
                workbook.save(byteIo)

                record = self.env['ir.attachment'].create({
                    'name': self.name,
                    'type': 'binary',
                    'datas': base64.b64encode(byteIo.getvalue()),
                    'datas_fname': '%s.xls'%self.name,
                    'res_model': 'account.invoice',
                    'mimetype': 'application/vnd.ms-excel'
                })

                self.send_mail(record)

    def send_mail(self,record):
        mail_pool = self.env['mail.mail']

        values = {}

        values.update({'subject': self.name})

        values.update({'email_to': self.emails})

        values.update({'body_html': self.body_content})

        # values.update({'attachment_ids':[(6, 0, record.id)]})

        # values.update({'body': 'body test'})

        # values.update(
        #     {'res_id': 'obj.id'})  # [optional] here is the record id, where you want to post that email after sending
        #
        # values.update({'model': ''
        #                Object Name})  # [optional] here is the object(like 'project.project')  to whose record id you want to post that email after sending

        msg_id = mail_pool.create(values)
        msg_id.attachment_ids = [(6, 0, [record.id])]

        # And then call send function of the mail.mail,

        if msg_id:
            mail_pool.send([msg_id])


    def write_table(self,worksheet,datas,row,group_iter,active_measures,groupby,parent=None):
        header_plain = xlwt.easyxf("pattern: pattern solid, fore_colour gray25;")
        header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
        bold = xlwt.easyxf("font: bold on;")

        for i,data in enumerate(datas[group_iter]):
            grouped = True
            if group_iter == 0:
                grouped =True
            else:
                for j in range(group_iter-1):
                    if data[groupby[j]] != parent[groupby[j]]:
                        grouped = False
                        break
            if grouped:
                tab = ''
                for x in range(group_iter):
                    tab+='     '
                if group_iter== 0:
                    worksheet.write(row, 0, u'Tổng',header_plain)
                else:
                    worksheet.write(row,0,u'%s'%(tab+data[groupby[group_iter-1]]),header_plain)
                if len(datas)>group_iter+1:
                    for j, header_row in enumerate(active_measures):
                        if type(data[header_row]) is not unicode:
                            worksheet.write(row, j + 1,u'%s'%(data[header_row]),bold)
                    row = row+1
                    row = self.write_table(worksheet,datas,row,group_iter+1,active_measures,groupby,data)
                else:
                    for j, header_row in enumerate(active_measures):
                        worksheet.write(row, j + 1,u'%s'%(data[header_row]))
                    row = row + 1
        return row
