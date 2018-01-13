# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
from tempfile import TemporaryFile, NamedTemporaryFile
from io import BytesIO
from datetime import datetime, date
from docxtpl import DocxTemplate, InlineImage, CheckedBox, CheckBox, RichText, Tick
from odoo.addons.hh_intern.models import intern_utils
_logger = logging.getLogger(__name__)

class MyDocument(models.Model):
    _name = 'intern.document'
    _description = u'Các loại văn bản, báo cáo'
    name = fields.Char("Tên", required=True)
    note = fields.Text("Ghi chú")
    file_name = fields.Char("Tên file")
    attachment = fields.Binary('Văn bản mẫu', required=True)
#
class Invoice(models.Model):
    _name = 'intern.invoice'
    _description = u'Tạo đơn hàng'

    name = fields.Char("Tên", required=True)
    name_of_guild = fields.Char("Tên nghiệp đoàn")
    enterprise = fields.Char("Tên xí nghiệp")

    order = fields.Char()


    @api.model
    def _default_document(self):
        return self.env['intern.document'].search([('name', '=', 'CV')], limit=1)

    document = fields.Many2one('intern.document', 'Văn bản',default=_default_document)
    interns = fields.Many2many('intern.intern')
                               # , domain=lambda self:self._getCurrentUser)

    # @api.model
    # def create(self, vals):
    #     # if 'interns' not in vals:
    #     #     raise UserError(_('Chua chon intern'))
    #     # if 'document' not in vals:
    #     #     raise UserError(_('Chua chon document'))
    #     _logger.info("AAAA %i" %vals['document'])
    #     # attachment = self.env['ir.attachment'].search([('res_model', '=', 'intern.document'), ('res_id', '=', vals['document'])])
    #
    #
    #     return super(Invoice, self).create(vals)

    # @api.model
    # def _getCurrentUser(self):
    #     return "('','=','user_access')"

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(Invoice, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'form':
    #         doc = etree.XML(res['arch'])
    #         _logger.info("VIEW_ID " +str(view_id))
    #         nodes = doc.xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[2]/ul/li/a")
    #         nodes[0].set('string', 'My dynamic label')
    #         res['arch'] = etree.tostring(doc)
    #     return res

    @api.multi
    def read(self, fields= None, load='_classic_read'):
        res = super(Invoice,self).read(fields=fields,load=load)
        # if res:
        #     for t in res:
        #         _logger.info("TT" +str(t))
        if res:
            if len(res) == 1:
                if 'order' in res[0] and 'interns' in res[0] and res[0]['order'] and res[0]['interns']:
                    # _logger.info("AAAA %s" %(res[0]['order']))
                    ids = []
                    for intern in self.interns:
                        ids.append(intern.id)
                    list = self.env['intern.intern'].search([('id','in',ids)],order="%s"%(res[0]['order']))
                    ids_new = []
                    for i in list:
                        ids_new.append(i.id)
                    res[0]['interns'] = ids_new
        return res



    @api.multi
    def create_doc(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=intern.invoice&id=%s&filename=doc_cv.zip' % (
            self.id),
            'target': 'self',}


    # def createHeaderDoc(self,interns):
    #     document = Document()
    #     section = document.sections[0]
    #     print section.orientation
    #     section.orientation = WD_ORIENTATION.LANDSCAPE
    #     print section.orientation
    #     new_height = section.page_width
    #     section.page_width = section.page_height
    #     section.page_height = new_height
    #
    #     table = document.add_table(rows=len(interns)+1, cols=5, style='Table Grid')
    #
    #     self.set_column_width(table.columns[0], Cm(1))
    #
    #     for idx, item in enumerate(table.rows):
    #         row = table.rows[idx]
    #         if idx == 0:
    #             row.cells[0].text = "STT"
    #             row.cells[1].text = self.getFieldString("intern.intern","name")
    #             row.cells[2].text = "Ngay sinh" #self.getFieldString("intern.intern","date_of_birth")
    #             row.cells[3].text = self.getFieldString("intern.intern","province")
    #             row.cells[4].text = self.getFieldString("intern.intern","address")
    #             continue
    #
    #         intern = interns[idx-1]
    #         # print("   "+intern.name   + " "  + interns[idx-1])
    #         row.cells[0].text = str(idx)
    #         row.cells[1].text = intern.name
    #         row.cells[2].text = intern_utils.date_time_in_jp(intern.day,intern.month,intern.year)
    #         row.cells[3].text = intern.province.name
    #         row.cells[4].text = intern.address
    #
    #     return document

    def createHeaderDoc(self):
        docs = self.env['intern.document'].search([('name', '=', "CV_HEAD")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}
            table_interns = []
            for i,intern in enumerate(self.interns):
                info = {}
                info['stt'] = str(i+1)
                info['htk'] = intern.name_without_signal.upper()
                info['htn'] = intern.name_in_japan
                if intern.gender == 'nu':
                    info['gt'] = u'女'
                else:
                    info['gt'] = u'男'
                info['ns'] = intern_utils.date_time_in_jp(intern.day,intern.month,intern.year)
                info['t'] = str((datetime.now().year)+1 - int(intern.year))
                info['nm'] = intern.blood_group
                info['tlt'] = intern.vision_left
                info['tlp'] = intern.vision_right
                if intern.preferred_hand == '0':
                    info['tt'] = u'右'
                else:
                    info['tt'] = u'左'
                info['cc'] = str(intern.height)
                info['cn'] = str(intern.weight)
                info['iq'] = "%s%%"%intern.iq_percentage
                info['ktk'] = intern.check_kureperin
                info['hn']  = intern.marital_status.name_in_jp
                info['pro'] = intern_utils.no_accent_vietnamese(intern.province.name).upper()
                info['bc'] = intern.certification.name_in_jp
                table_interns.append(info)

            context['xn'] = self.enterprise
            context['nd'] = self.name_of_guild
            context['now'] = intern_utils.date_time_in_jp(datetime.now().day+1,datetime.now().month +1,datetime.now().year+1)
            context['tbl_intern'] = table_interns
            tpl.render(context)

            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile
        return None



    def set_column_width(self,column, width):
        for cell in column.cells:
            cell.width = width

    def getFieldString(self, model_name, name):
        model_obj = self.env['ir.model']
        field_label_list = []
        model_id = model_obj.search([('model', '=', model_name)])
        if model_id:
            print model_id[0]
            field_ids = self.env['ir.model.fields'].search([('model_id', '=', model_id[0].id), ('name', '=', name)])
            if field_ids:
                return field_ids[0].field_description
        return ""


    # def getFixAllPredefineImage(self,document):
    #     stream = BytesIO(document.attachment.decode("base64"))
    #     doc = Document(stream)
    #     list_image = []
    #     for i, shape in enumerate(doc.inline_shapes):
    #         if shape.type == WD_INLINE_SHAPE.PICTURE:
    #             inline = shape._inline
    #             rId = inline.xpath('./a:graphic/a:graphicData/pic:pic/pic:blipFill/a:blip/@r:embed')[0]
    #             image_part = doc.part.related_parts[rId]
    #             list_image.append(image_part.blob)

    def calculate_age(self,born):
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def createCVDoc(self, document, intern, index):
        stream = BytesIO(document.attachment.decode("base64"))
        tpl = DocxTemplate(stream)
        context = {}
        if intern.avatar is not None:
            streamAvatar = BytesIO(intern.avatar.decode("base64"))
            # context['aa'] = InlineImage(tpl, streamAvatar, width=Mm(20))
            tpl.replace_pic('avatar.jpg',streamAvatar)

        context['stt'] = str(index+1)
        # context['ht'] = intern.name
        context['htk'] = intern.name_without_signal.upper()

        if intern.gender == 'nu':
            context['gt'] = '女'
        else:
            context['gt'] = '男'
        context['t'] = str((datetime.now().year)+1- int(intern.year))

        if intern.marital_status:
            context['hn'] = intern.marital_status.name_in_jp
        if intern.name_in_japan:
            context['htn'] = intern.name_in_japan
        if intern.date_of_birth:
            context['ns'] = intern_utils.date_time_in_jp(intern.day,intern.month,intern.year)
        if intern.address:
            context['dc'] = (intern.address + " - " + intern_utils.no_accent_vietnamese(intern.province.name)).upper()
            context['kc'] = intern.province.getDistanceString()
        if intern.phone_number:
            context['sdt'] = intern.phone_number
        if intern.height:
            context['cc'] = str(intern.height)
        if intern.weight:
            context['cn'] = str(intern.weight)
        if intern.vision_left:
            context['tl'] = intern.vision_left + " - " + intern.vision_right


        if intern.blindness:
            context['cmm'] = CheckedBox().init(24)
            context['kmm'] = CheckBox().init(24)
        else:
            context['cmm'] = CheckBox().init(24)
            context['kmm'] = CheckedBox().init(24)

        if intern.smoking:
            context['cht'] = CheckedBox().init(24)
            context['kht'] = CheckBox().init(24)
        else:
            context['cht'] = CheckBox().init(24)
            context['kht'] = CheckedBox().init(24)

        if intern.preferred_hand == '0':
            context['ptt'] = CheckedBox().init(24)
            context['ttt'] = CheckBox().init(24)
        else:
            context['ptt'] = CheckBox().init(24)
            context['ttt'] = CheckedBox().init(24)

        if intern.surgery:
            context['chx'] = CheckedBox().init(24)
            context['khx'] = CheckBox().init(24)
            context['hxnd'] = intern.surgery_content
        else:
            context['chx'] = CheckBox().init(24)
            context['khx'] = CheckedBox().init(24)

        if intern.drink_alcohol:
            context['crb'] = CheckedBox().init(24)
            context['krb'] = CheckBox().init(24)
        else:
            context['crb'] = CheckBox().init(24)
            context['krb'] = CheckedBox().init(24)

        if intern.specialized:
            _logger.info("Chuyen nganh")
            context['chn'] = intern.specialized
        if intern.favourite:
            context['st'] = intern.favourite
        if intern.strong:
            context['dm'] = intern.strong
        if intern.weak:
            context['dy'] = intern.weak
        if intern.teammate:
            context['kns'] = u'有'
        else:
            context['kns'] = u'無'

        if intern.cooking:
            context['na'] = u'可'
        else:
            context['na'] = u'不可'

        if intern.diseases:
            context['bt'] = u'有'
        else:
            context['bt'] = u'無'
        if intern.blood_group:
            context['nm'] = intern.blood_group
        if intern.check_kureperin:
            context['ktk'] = intern.check_kureperin
        if intern.iq_percentage:
            if u'%' in intern.iq_percentage:
                context['iq'] = intern.iq_percentage
            else:
                context['iq'] = intern.iq_percentage+u"%"
        if intern.family_income:
            context['tng'] = intern.family_income
        if intern.motivation:
            context['dl'] = intern.motivation
        if intern.income_after_three_year:
            context['bn']= intern.income_after_three_year
        if intern.job_after_return:
            context['vn'] = intern.job_after_return
        if intern.prefer_object:
            context['mg'] = intern.prefer_object
        if intern.memory:
            context['kn'] = intern.memory
        if intern.valuable:
            context['qg'] = intern.valuable

        context['hm'] = CheckBox().init(20)
        context['hs'] = CheckBox().init(20)
        context['lb'] = CheckBox().init(20)
        if intern.education_status:
            if intern.education_status == '1':
                context['hs'] = CheckedBox().init(20)
            elif intern.education_status == '2':
                context['hm'] = CheckedBox().init(20)
            elif intern.education_status == '3':
                context['lb'] = CheckedBox().init(20)
            context['edct'] = intern.education_content

        table_education = []
        for education in intern.educations:
            info = {}
            if education.month_start:
                info['nbd'] = intern_utils.date_time_in_jp(month=education.month_start, year=education.year_start)
            else:
                info['nbd'] = intern_utils.date_time_in_jp(year=education.year_start)
            if education.month_end:
                info['nkt'] = intern_utils.date_time_in_jp(month=education.month_end, year=education.year_end)
            else:
                info['nkt'] = intern_utils.date_time_in_jp(year=education.year_end)
            info['tt'] = intern_utils.no_accent_vietnamese(education.school).upper()
            info['lt'] = education.school_type.name_in_jp
            info['cn'] = education.specialization
            info['bc'] = education.certificate.name_in_jp
            if education.graduated:
                info['tn'] = u'卒業'
            else:
                info['tn'] = u'未卒業'

            table_education.append(info)

        context['tbl_educations'] = table_education

        table_employment = []
        for employment in intern.employments:
            info = {}
            if employment.month_start:
                info['nbd'] = intern_utils.date_time_in_jp(month=employment.month_start, year=employment.year_start)
            else:
                info['nbd'] = intern_utils.date_time_in_jp(year=employment.year_start)
            if employment.month_end:
                info['nkt'] = intern_utils.date_time_in_jp(month=employment.month_end, year=employment.year_end)
            else:
                info['nkt'] = intern_utils.date_time_in_jp(year=employment.year_end)
            info['ct'] = employment.company
            info['cv'] = employment.description
            table_employment.append(info)

        context['tbl_employ'] = table_employment

        table_family = []
        for i,person in enumerate(intern.family_members):
            if i < 5:
                context['p%dht'%(i+1)] = intern_utils.no_accent_vietnamese(person.name).upper()
                context['p%dqh'%(i+1)] = person.relationship
                context['p%ddt'%(i+1)] = str((datetime.now().year)+1- int(person.birth_year))
                # context['p%ddt' % (i + 1)] = person.ages
                context['p%dnn' % (i + 1)] = person.job
                if person.live_together:
                    context['p%dsc' % (i + 1)] = Tick()
                else:
                    context['p%dsr' % (i + 1)] = Tick()
            else:

                if person.live_together:
                    table_family.append({'ht': intern_utils.no_accent_vietnamese(person.name).upper(), 'qh': person.relationship,
                                         'dt': str((datetime.now().year)+1- int(person.birth_year)),
                                         # 'dt': person.ages,
                                             'nn': person.job, 'sc': Tick(),'sr':''})
                else:
                    table_family.append({'ht': intern_utils.no_accent_vietnamese(person.name).upper(), 'qh': person.relationship,
                                         'dt': str((datetime.now().year) + 1 - int(person.birth_year)),
                                         # 'dt': person.ages,
                                         'nn': person.job, 'sc': '', 'sr': Tick()})
        context['tbl_family'] = table_family

        if intern.family_member_in_jp:
            context['cnt'] = CheckedBox().init(24)
            context['knt'] = CheckBox().init(24)
            context['nton'] = intern.family_member_in_jp
        else:
            context['cnt'] = CheckBox().init(24)
            context['knt'] = CheckedBox().init(24)

        if intern.family_accept:
            context['gdy'] = CheckedBox().init(24)
            context['gpd'] = CheckBox().init(24)
        else:
            context['gdy'] = CheckBox().init(24)
            context['gpd'] = CheckedBox().init(24)

        tpl.render(context)

        # byteIoRespond = BytesIO()
        # tpl.save(byteIoRespond)
        # byteIoRespond.seek(0)
        # return byteIoRespond
        tempFile = NamedTemporaryFile(delete=False)
        tpl.save(tempFile)
        tempFile.flush()
        tempFile.close()
        return tempFile

    @api.model
    def on_order_changed(self,id, column, state):
        _logger.info("TEST " + str(state) + " " + str(id))
        invoice = self.env['intern.invoice'].browse(int(id))
        if invoice:
            _logger.info("TEST " + str(invoice.order))
            if state==0:
                invoice.write({'order': "%s"%(column)})
            else:
                invoice.write({'order': "%s desc" % (column)})


            # def createCVDoc(self,document, intern,index):
    #     # _logger.info('[%i]' %intern_id)
    #     # intern = self.env['intern.intern'].browse(intern_id.id)
    #     # file_like_io = StringIO(base64.decodestring(attachment[0].datas))
    #
    #     if document.file_name and document.file_name.endswith(".docx"):
    #
    #         _logger.info("vao tao nao")
    #         stream = BytesIO(document.attachment.decode("base64"))
    #         # temp = TemporaryFile('w+')
    #         # open('test.pdf', 'wb').write(attachment[0].datas.decode("base64"))
    #         # intern = self.env['intern.intern'].browse(intern_id)
    #         streamAvatar = None
    #         if intern.avatar is not None:
    #             streamAvatar = BytesIO(intern.avatar.decode("base64"))
    #         # f = open('test.png', 'wb')
    #         # f.write(streamAvatar)
    #         # f.close()
    #         doc = Document(stream)
    #
    #
    #         # tables = doc.tables
    #         # p = tables[0].rows[0].cells[0].add_paragraph()
    #         # p.text = '{{avatar%d}}'% index
    #
    #
    #         # r = p.add_run()
    #         #
    #         # if streamAvatar is not None:
    #         #     r.add_picture(streamAvatar, width=Inches(4.0), height=Inches(1.7))
    #
    #         for table in doc.tables:
    #             for row in table.rows:
    #                 for cell in row.cells:
    #                     for paragraph in cell.paragraphs:
    #                         paragraph.text = paragraph.text.replace("{stt}", str(index+1))
    #
    #                         # if '{co_mu_mau}' in paragraph.text:
    #                         #     if intern.blindness:
    #                         #         paragraph.text = paragraph.text.replace("{co_mu_mau}", u'☒ 有')
    #                         #     else:
    #                         #         paragraph.text = paragraph.text.replace("{co_mu_mau}", u'□ 有')
    #
    #                         if '{name}' in paragraph.text:
    #                             paragraph.text = paragraph.text.replace("{name}", intern.name)
    #
    #                         if '{cooking}' in paragraph.text:
    #                             _logger.info("AAAAAAAA")
    #                             paragraph.text = paragraph.text.replace("{cooking}", u'☐')
    #
    #
    #         for paragraph in doc.paragraphs:
    #             if '{name}' in paragraph.text:
    #                 print paragraph.text
    #                 paragraph.text = paragraph.text.replace("{name}", intern.name)
    #
    #             if '{cooking}' in paragraph.text:
    #                 _logger.info("BBBB")
    #                 paragraph.text = paragraph.text.replace("{cooking}", u'☐')
    #
    #         return doc
    #
    #     return None
            # zin = zipfile.ZipFile(doc., 'r')
            # zout = zipfile.ZipFile('test1.docx', 'w')
            # for item in zin.infolist():
            #     buffer = zin.read(item.filename)
            #     if (item.filename == 'word/document.xml'):
            #         res = buffer.decode("utf-8")
            #         res = res.replace("{name}", "KKKK")
            #         buffer = res.encode("utf-8")
            #     zout.writestr(item, buffer)
            # zout.close()
            # zin.close()


        # elif attachment.datas_fname.endswith(".xlsx"):
        #     stream = BytesIO(attachment.datas.decode("base64"))
            # wb = openpyxl.load_workbook(stream)
            # ws = wb.active
            # for cells in ws.rows:
            #     for cell in cells:
            #         if "{name}" in cell.value:
            #             cell.value = cell.value.replace("{name}", "KKKK")
            # wb.save('test333.xlsx')

    # @api.multi
    # def write(cr, uid, ids, vals, context=None):
    #     # your code
    #     super(stock_picking_out, self).wite(cr, uid, ids, vals, context=context)
    #     # your code
    #     return False


# def addCheckbox(para, box_id, name):
#     run = para.add_run()
#     tag = run._r
#     fld = docx.oxml.shared.OxmlElement('w:fldChar')
#     fld.set(docx.oxml.ns.qn('w:fldCharType'), 'begin')
#     fldData = docx.oxml.shared.OxmlElement('w:fldData')
#
#     fldData.text = '/////2UAAAAUAAYAQwBoAGUAYwBrADEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
#     fldData.set(docx.oxml.ns.qn('xml:space'), 'preserve')
#     fld.append(fldData)
#     tag.append(fld)
#
#     run2 = para.add_run()
#     tag2 = run2._r
#     start = docx.oxml.shared.OxmlElement('w:bookmarkStart')
#     start.set(docx.oxml.ns.qn('w:id'), str(box_id))
#     start.set(docx.oxml.ns.qn('w:name'), name)
#     tag2.append(start)
#
#     run3 = para.add_run()
#     tag3 = run3._r
#     instr = docx.oxml.OxmlElement('w:instrText')
#     instr.text = 'FORMCHECKBOX'
#     tag3.append(instr)
#
#     run4 = para.add_run()
#     tag4 = run4._r
#     fld2 = docx.oxml.shared.OxmlElement('w:fldChar')
#     fld2.set(docx.oxml.ns.qn('w:fldCharType'), 'end')
#     tag4.append(fld2)
#
#     run5 = para.add_run()
#     tag5 = run5._r
#     end = docx.oxml.shared.OxmlElement('w:bookmarkEnd')
#     end.set(docx.oxml.ns.qn('w:id'), str(box_id))
#     end.set(docx.oxml.ns.qn('w:name'), name)
#     tag5.append(end)
#     return