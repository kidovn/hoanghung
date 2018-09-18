# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

import os
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import xlwt
import json
import ast
import base64
from io import BytesIO, StringIO
import logging
import re
from datetime import datetime,date

from odoo.addons.mail.models import mail_template

import sys
_logger = logging.getLogger(__name__)

class IrCron(models.Model):
    _name='hh.cron'
    _inherits = {'ir.cron': 'cron_job_id'}
    # name = fields.Char('Tên báo cáo')
    cron_job_id = fields.Many2one('ir.cron', string='Cron job', auto_join=True,  ondelete="cascade", required=True)


    body_content = fields.Text('Nội dung email')

    emails = fields.Char('Địa chỉ email nhận')
    emails_cc = fields.Char('Địa chỉ email cc')

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
            cron.method_direct_trigger_demo()

    def method_direct_trigger_demo(self):
        # _logger.info("TESTTT------ %d"%date.today().weekday())
        if date.today().weekday() == 6:
            return
        reload(sys)
        sys.setdefaultencoding("utf-8")

        template = self.env['mail.template'].search([('name','=','REPORT TEMPLATE')])[0]

        variables = {
            'format_date': lambda date, format=False, context=self._context: mail_template.format_date(self.env, date, format),
            'format_tz': lambda dt, tz=False, format=False, context=self._context: mail_template.format_tz(self.env, dt, tz, format),
            'format_amount': lambda amount, currency, context=self._context: mail_template.format_amount(self.env, amount, currency),
            'user': self.env.user,
            'ctx': self._context,  # context kw would clash with mako internals
        }

        headers= []
        measures = []
        if not self._context:
            self._context = {'lang': u'vi_VN'}
        if self.report:
            # _logger.info("DO NOTHING %s"%self.report.context.replace("u\\'",'"').replace("'",'"').replace('u"','"'))
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

                if self.report.model_id == 'intern.invoice':
                    fields.append('color_notice')


                datas.append(self.env[self.report.model_id].read_group(domains, fields, tmp_groupbys,lazy=False))
                for group in groupby:
                    tmp_groupbys.append(group)
                    datas.append(self.env[self.report.model_id].read_group(domains,fields,tmp_groupbys,lazy=False))



                for i, group in enumerate(groupby):
                    if ':' in group:
                        group = group.split(':')[0]
                    if group == 'custom_id' and self.report.model_id == 'intern.invoice':
                        continue
                    headers.append(fields_model[group])
                    measures.append(group)

                for i, header_row in enumerate(active_measures):
                    headers.append(fields_model[header_row])
                    measures.append(header_row)

        body = []

        if self.report.model_id == 'intern.invoice' and 'date_exam_short' in active_measures:
            # index = 0
            # for i, x in enumerate(headers):
            #     if x
            def tryconvert(date_str):
                try:
                    return datetime.strptime(date_str,'%d-%m-%Y')
                except ValueError:
                    return datetime(1, 1, 1)
            datas[1] = sorted(datas[1],key=lambda r: (tryconvert(r['date_exam_short'][0])))

        color = None
        if self.report.model_id == 'intern.invoice':
            color = []

        body, row, color = self.write_body(self.report.model_id,body,datas,0,1,active_measures,groupby,color,None)

        # for i,data in enumerate(datas[1]):
        #     for j, tmp in enumerate(data):
        #         if type(data[tmp]) is list:
        #             datas[1][i][tmp] = datas[1][i][tmp][0]
        #         elif type(data[tmp]) is tuple:
        #             datas[1][i][tmp] = datas[1][i][tmp][1]

        for i, data in enumerate(datas[0]):
            for j, tmp in enumerate(data):
                if type(data[tmp]) is list:
                    datas[0][i][tmp] = ''
                elif type(data[tmp]) is unicode:
                    datas[0][i][tmp] = ''
                elif type(data[tmp]) is tuple:
                    datas[0][i][tmp] = datas[0][i][tmp][1]


        variables['headers'] = headers
        variables['measures'] = measures
        variables['objects'] = body
        # variables['objects'] = ['1','2','3']
        variables['email_template'] = template
        variables['footer'] = datas[0][0]
        if color is not None:
            variables['color'] = color
        else:
            variables['color'] = False

        # return self.env['report'].render('hh_automation_report.report_intern_pass_view', values=docargs)

        # try:
        render_result = template.body_view_id.render(variables)
        # except Exception:
        #     _logger.info("Failed to render template %r using values %r" % (template, variables), exc_info=True)
        #     raise UserError(_("Failed to render template %r using values %r") % (template, variables))


        if render_result == u"False":
            render_result = u""

        render_result = "%s<div>%s</div>"%(self.body_content,render_result)
        if self.env.user and self.env.user.signature:
            render_result+="<div><br></div>--<br>%s"%self.env.user.signature

        mail_pool = self.env['mail.mail']

        values = {}
        emails = self.emails.split(',')
        for i,email in enumerate(emails):
            if '<' in email and '>' in email:
                emails[i] = email[email.index('<')+1:email.index('>')]
        values.update({'subject': self.build_subject()})
        values.update({'email_to': ','.join(emails)})

        if self.emails_cc:
            emails_cc = self.emails_cc.split(',')
            for i, email in enumerate(emails_cc):
                if '<' in email and '>' in email:
                    emails_cc[i] = email[email.index('<') + 1:email.index('>')]

            values.update({'email_cc': ','.join(emails_cc)})


        values.update({'body_html': render_result})
        msg_id = mail_pool.create(values)
        if msg_id:
            mail_pool.send([msg_id])

    def write_body(self,model_id,body,datas,row,group_iter,active_measures,groupby,color,parent=None):

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
                # counter = 0
                body.append([])
                # worksheet.write(row, 0, u'%d' % row)
                for j in range(0, group_iter-1):
                    body[row].append('')
                if model_id != 'intern.invoice' or  groupby[group_iter - 1] != 'custom_id':
                    if type(data[groupby[group_iter - 1]]) == tuple:
                        # worksheet.write(row, group_iter, u'%s' % (tab + data[groupby[group_iter - 1]][1]))
                        body[row].append(tab + data[groupby[group_iter - 1]][1])
                    elif not data[groupby[group_iter - 1]]:
                        body[row].append('Không xác định')
                        # tab + data[groupby[group_iter - 1]][1]) tab+ u'Không xác định')
                    else:
                        body[row].append(tab + data[groupby[group_iter - 1]])
                        # worksheet.write(row, group_iter, u'%s' % (tab + data[groupby[group_iter - 1]]))
                # counter +=1
                for j in range(group_iter, len(groupby)):
                    body[row].append('')
                if len(datas)>group_iter+1:
                    for j, header_row in enumerate(active_measures):
                        if type(data[header_row]) is list:
                            # worksheet.write(row, j + 2,u'%s'%(data[header_row][0]))
                            # worksheet.write(row, j + len(groupby)+1,'')
                            body[row].append('')
                        elif type(data[header_row]) is not unicode:
                            # worksheet.write(row, j + len(groupby)+1,u'%s'%(data[header_row]),bold)
                            body[row].append(data[header_row])
                        else:
                            body[row].append('')
                        # counter+=1
                    row = row+1
                    body, row, color = self.write_body(model_id,body,datas,row,group_iter+1,active_measures,groupby,color,data)
                else:
                    for j, header_row in enumerate(active_measures):
                        if type(data[header_row]) is list:
                            body[row].append((',').join(data[header_row]))
                        elif type(data[header_row]) is int or type(data[header_row]) is float:
                            body[row].append('%d' % data[header_row])
                        elif type(data[header_row]) is bool and data[header_row] is False:
                            body[row].append('')
                        else:
                            body[row].append('%s'%data[header_row])
                        # counter+=1
                    row = row + 1
                    if color is not None:
                        color.append(data['color_notice'])
        return body, row, color

    def build_subject(self):
        subject = self.name.replace('datetime.today()',datetime.today().strftime('%d/%m/%Y'))
        return subject


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

                header_plain = xlwt.easyxf("pattern: pattern solid, fore_colour light_green;")
                footer_plain = xlwt.easyxf("pattern: pattern solid, fore_colour gray25;")
                worksheet.write(0, 0, u'STT', header_plain)
                for i, group in enumerate(groupby):
                    worksheet.write(0, i+1, u'%s' % fields_model[group]['string'], header_plain)

                for i, header_row in enumerate(active_measures):
                    worksheet.write(0, i + len(groupby)+1, u'%s'%(fields_model[header_row]['string']),header_plain)

                # row_counter = 1
                # worksheet.write(row_counter,0,'Tổng')
                # for i in
                # for i,header_row in enumerate(active_measures):
                #     worksheet.write(1, i+1, 'Tổng')

                row = self.write_table(worksheet,datas,1,1,active_measures,groupby,None)
                # workbook.save("trial.xls")

                #Write footer total
                if datas and len(datas)>0 and len(datas[0])>0:
                    worksheet.write(row,1,u'Tổng',footer_plain)
                    for i, group in enumerate(groupby):
                        if i > 0:
                            worksheet.write(row, i + 1,'',footer_plain)

                    for j, header_row in enumerate(active_measures):
                        if type(datas[0][0][header_row]) is int:
                            worksheet.write(row, j + len(groupby) + 1, '%d'%datas[0][0][header_row],footer_plain)
                        else:
                            worksheet.write(row, j + len(groupby) + 1,'',footer_plain)

                        # if type(datas[0][0][header_row]) is list:
                        #
                        # else:
                        #     worksheet.write(row, j + len(groupby)+1,u'%s'%(datas[0][0][header_row]))


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

        values.update({'body_html': self.build_body_content()})
        msg_id = mail_pool.create(values)
        msg_id.attachment_ids = [(6, 0, [record.id])]
        if msg_id:
            mail_pool.send([msg_id])

    def build_body_content(self):
        body = self.body_content
        body+= '<div><table border="0" cellspacing="0" cellpadding="0" width="940"><tbody>'

        #Build data
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

                body+='<tr><td width="40" style="border-width:1pt;border-style:solid;border-color:windowtext windowtext black;background:rgb(155,187,89)"><div style="text-align:center;"><b style="font-weight:bold;">' \
                      '<span style="font-size:9pt">STT</span></b></div></td>'
                for i, group in enumerate(groupby):
                    body+= u'<td style="border-width:1pt;border-style:solid;border-color:windowtext windowtext black;background:rgb(155,187,89)"><div style="text-align:center;"><b style="font-weight:bold;"><span style="font-size:9pt">%s</span></b></div></td>' % fields_model[group]['string']

                for i, header_row in enumerate(active_measures):
                    body += u'<td style="border-width:1pt;border-style:solid;border-color:windowtext windowtext black;background:rgb(155,187,89)"><div style="text-align:center;"><b style="font-weight:bold;"><span style="font-size:9pt">%s</span></b></div></td>' % (fields_model[header_row]['string'])

                body+="</tr>"

                #body table
                body, row = self.write_table_html(body, datas,1,1,active_measures,groupby,None)


        body += '</tbody></table></div>'
        return body


    def write_table_html(self,body,datas,row,group_iter,active_measures,groupby,parent=None):

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
                body += '<tr><td style="border-right:1pt solid windowtext;border-bottom:1pt solid windowtext;border-left:1pt solid windowtext;border-top:none;"><div style="text-align:center;"><span style="font-size:9pt">%d</span></div></td>'% row
                # worksheet.write(row, 0, u'%d' % row)
                if type(data[groupby[group_iter - 1]]) == tuple:
                    # worksheet.write(row, group_iter, u'%s' % (tab + data[groupby[group_iter - 1]][1]))
                    body += '<td style="border-right:1pt solid windowtext;border-bottom:1pt solid windowtext;border-left:1pt solid windowtext;border-top:none;"><div style="text-align:center;"><span style="font-size:9pt">%s</span></div></td>'% (tab + data[groupby[group_iter - 1]][1])
                elif not data[groupby[group_iter - 1]]:
                    body += '<td style="border-right:1pt solid windowtext;border-bottom:1pt solid windowtext;border-left:1pt solid windowtext;border-top:none;"><div style="text-align:center;"><span style="font-size:9pt">%s</span></div></td>' % ('Không xác định')
                    # tab + data[groupby[group_iter - 1]][1]) tab+ u'Không xác định')
                else:
                    body += '<td style="border-right:1pt solid windowtext;border-bottom:1pt solid windowtext;border-left:1pt solid windowtext;border-top:none;"><div style="text-align:center;"><span style="font-size:9pt">%s</span></div></td>' % (
                            tab + data[groupby[group_iter - 1]])
                    # worksheet.write(row, group_iter, u'%s' % (tab + data[groupby[group_iter - 1]]))

                if len(datas)>group_iter+1:
                    for j, header_row in enumerate(active_measures):
                        if type(data[header_row]) is list:
                            # worksheet.write(row, j + 2,u'%s'%(data[header_row][0]))
                            # worksheet.write(row, j + len(groupby)+1,'')
                            body += '<td style="border-right:1pt solid windowtext;border-bottom:1pt solid windowtext;border-left:1pt solid windowtext;border-top:none;"><div style="text-align:center;"><span style="font-size:9pt"></span></div></td>'
                        elif type(data[header_row]) is not unicode:
                            # worksheet.write(row, j + len(groupby)+1,u'%s'%(data[header_row]),bold)
                            body += '<td style="border-right:1pt solid windowtext;border-bottom:1pt solid windowtext;border-left:1pt solid windowtext;border-top:none;"><div style="text-align:center;"><span style="font-size:9pt">%s</span></div></td>'%(data[header_row])
                    row = row+1
                    body+='</tr>'
                    body, row = self.write_table_html(body,datas,row,group_iter+1,active_measures,groupby,data)
                else:
                    for j, header_row in enumerate(active_measures):
                        if type(data[header_row]) is list:
                            body += '<td style="border-right:1pt solid windowtext;border-bottom:1pt solid windowtext;border-left:1pt solid windowtext;border-top:none;"><div style="text-align:center;"><span style="font-size:9pt">%s</span></div></td>' % (
                                (',').join(data[header_row]))
                            # worksheet.write(row, j + len(groupby)+1, u'%s' % (',').join(data[header_row]))
                        else:
                            body += '<td style="border-right:1pt solid windowtext;border-bottom:1pt solid windowtext;border-left:1pt solid windowtext;border-top:none;"><div style="text-align:center;"><span style="font-size:9pt">%s</span></div></td>' % ((data[header_row]))
                            # worksheet.write(row, j + len(groupby)+1,u'%s'%(data[header_row]))
                    body += '</tr>'
                    row = row + 1
        return body, row



    # def send_mail(self,record):
    #     mail_pool = self.env['mail.mail']
    #
    #     values = {}
    #
    #     values.update({'subject': self.name})
    #
    #     values.update({'email_to': self.emails})
    #
    #     values.update({'body_html': self.body_content})
    #
    #     # values.update({'attachment_ids':[(6, 0, record.id)]})
    #
    #     # values.update({'body': 'body test'})
    #
    #     # values.update(
    #     #     {'res_id': 'obj.id'})  # [optional] here is the record id, where you want to post that email after sending
    #     #
    #     # values.update({'model': ''
    #     #                Object Name})  # [optional] here is the object(like 'project.project')  to whose record id you want to post that email after sending
    #
    #     msg_id = mail_pool.create(values)
    #     msg_id.attachment_ids = [(6, 0, [record.id])]
    #
    #     # And then call send function of the mail.mail,
    #
    #     if msg_id:
    #         mail_pool.send([msg_id])


    def write_table(self,worksheet,datas,row,group_iter,active_measures,groupby,parent=None):
        header_plain = xlwt.easyxf("pattern: pattern solid, fore_colour light_green;")
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
                # for x in range(group_iter):
                #     tab+='     '
                # if group_iter== 0:
                #     # worksheet.write(row, 0, u'STT', header_plain)
                #     # worksheet.write(row, 1, u'%s'%first_groupby,header_plain)
                #     _logger.info("AAAA")
                # else:
                #     worksheet.write(row, 0, u'%d'%row)
                #     if type(data[groupby[group_iter-1]]) == tuple:
                #         worksheet.write(row, 1, u'%s' % (tab + data[groupby[group_iter - 1]][1]))
                #     elif not data[groupby[group_iter-1]]:
                #         worksheet.write(row, 1, tab)
                #     else:
                #         worksheet.write(row,1,u'%s'%(tab+data[groupby[group_iter-1]]))

                worksheet.write(row, 0, u'%d' % row)
                if type(data[groupby[group_iter - 1]]) == tuple:
                    worksheet.write(row, group_iter, u'%s' % (tab + data[groupby[group_iter - 1]][1]))
                elif not data[groupby[group_iter - 1]]:
                    worksheet.write(row, group_iter, tab+ u'Không xác định')
                else:
                    worksheet.write(row, group_iter, u'%s' % (tab + data[groupby[group_iter - 1]]))

                if len(datas)>group_iter+1:
                    for j, header_row in enumerate(active_measures):
                        if type(data[header_row]) is list:
                            # worksheet.write(row, j + 2,u'%s'%(data[header_row][0]))
                            worksheet.write(row, j + len(groupby)+1,'')
                        elif type(data[header_row]) is not unicode:
                            worksheet.write(row, j + len(groupby)+1,u'%s'%(data[header_row]),bold)
                    row = row+1
                    row = self.write_table(worksheet,datas,row,group_iter+1,active_measures,groupby,data)
                else:
                    for j, header_row in enumerate(active_measures):
                        if type(data[header_row]) is list:
                            worksheet.write(row, j + len(groupby)+1, u'%s' % (',').join(data[header_row]))
                        elif type(data[header_row]) is int or type(data[header_row]) is float:
                            worksheet.write(row, j + len(groupby) + 1, u'%d' % (data[header_row]))
                        elif type(data[header_row]) is bool and data[header_row] is False:
                            worksheet.write(row, j + len(groupby) + 1,'')
                        else:
                            worksheet.write(row, j + len(groupby)+1,u'%s'%(data[header_row]))
                    row = row + 1
        return row
