# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
from tempfile import TemporaryFile, NamedTemporaryFile
from io import BytesIO
from datetime import datetime, date
from docxtpl import DocxTemplate, InlineImage, CheckedBox, CheckBox, RichText, Tick
import intern_utils
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class Invoice(models.Model):
    _name = 'intern.invoice'
    _description = u'Đơn hàng'

    name = fields.Char("Tên đơn hàng", required=True)
    name_of_guild = fields.Char("Tên nghiệp đoàn")
    enterprise = fields.Char("Tên xí nghiệp")
    order = fields.Char()

    place_to_work = fields.Char("Địa điểm làm việc")
    legal_name = fields.Selection([('chauhung', 'Châu Hưng'), ('hoanghung', 'Hoàng Hưng'), ('tracodi', 'Tracodi')],
                                  'Pháp nhân')


    @api.model
    def _default_document(self):
        return self.env['intern.document'].search([('name', '=', 'CV')], limit=1)

    document = fields.Many2one('intern.document', 'Văn bản',default=_default_document)
    interns = fields.Many2many('intern.intern',string=u'Danh sách thi tuyển')

    # @api.model
    # @api.onchange('interns')
    # @api.depends('interns')
    # def _get_interns_pass(self):
    #     _logger.info("_get_interns_pass")
    #     # listId = []
    #     # for intern in self.interns:
    #     #     _logger.info("_get_interns_pass " + str(intern.pass_recruitment))
    #     #     if intern.pass_recruitment == '1':
    #     #         _logger.info("PASSS " + str(intern.id))
    #     #         self.interns_pass = [[4, intern.id]]
    #     #         listId.append(intern)
    #     # # self.interns_pass = [[4,listId]]
    #     # self.interns_pass = listId
    #     self.interns_pass = self.interns.filtered(lambda l:l.pass_recruitment == '1')

    interns_pass = fields.Many2many(relation='invoice_intern_pass_rel',comodel_name='intern.intern')
    # interns_pass = fields.Many2many(comodel_name='intern.intern',store=False,compute='_get_interns_pass')




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

                    try:
                        list = self.env['intern.intern'].search([('id','in',ids)],order="%s"%(res[0]['order']))
                        ids_new = []
                        for i in list:
                            ids_new.append(i.id)
                        res[0]['interns'] = ids_new
                    except:
                        _logger.info('order %s'%(res[0]['order']))
        return res

    @api.multi
    def create_proletter_doc(self):
        if self.interns_pass is None or len(self.interns_pass) is 0:
            raise ValidationError("Không có thực tập sinh nào trong danh sách trúng tuyển")

        error2 = ""
        if not self.dispatchcom1:
            error2 = error2 + u"- pháp nhân\n"
        if not self.guild:
            error2 = error2 + u"- nghiệp đoàn\n"
        if not self.enterprise_doc:
            error2 = error2 + u"- xí nghiệp\n"
        if self.year_expire==0:
            error2 = error2 + u"- thời hạn hợp đồng\n"

        if not self.person_sign_proletter\
                or not self.position_person_sign:
            error2 = error2+u"- người ký thư tiến cử\n"
        if not self.day_create_letter_promotion or not self.month_create_letter_promotion or not self.year_create_letter_promotion:
            error2 = error2 + u"- ngày làm thư tiến cử\n"
        if not self.job_en or not self.job_jp or not self.job_vi:
            error2 = error2 + u"- ngành nghề xin thư tiến cử\n"

        if not self.month_departure_doc or not self.year_departure_doc:
            error2 = error2 + u"- ngày nộp xuất cảnh dự kiến\n"

        if error2:
            raise ValidationError(u"Thiếu thông tin bổ sung cho hồ sơ: \n%s" % error2)


        if not self.dispatchcom1.name_jp or not self.dispatchcom1.name_en or not self.dispatchcom1.name \
            or not self.dispatchcom1.director or not self.dispatchcom1.position_director or not self.dispatchcom1.position_director_vi \
            or not self.dispatchcom1.address_vi \
                or not self.dispatchcom1.address_en \
            or not self.dispatchcom1.phone_number:

            raise ValidationError(u"Thiếu thông tin của pháp nhân")

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_proletter_document?model=intern.invoice&id=%s&filename=ThuTienCu.zip' % (
                self.id),
            'target': 'self', }


    @api.multi
    def create_extern_doc(self):
        if self.interns_pass is None or len(self.interns_pass) is 0:
            raise ValidationError("Không có thực tập sinh nào trong danh sách trúng tuyển")
        for itern in self.interns_pass:
            error = ""
            if not itern.name:
                error = error+u'- tên tiếng Việt\n'
            if not itern.name_in_japan:
                error = error + u'- tên tiếng Nhật\n'
            if not itern.day or not itern.month or not itern.year:
                error = error + u'- ngày sinh\n'
            if not itern.gender:
                error = error + u'- giới tính\n'
            if not itern.marital_status:
                error = error + u'- tình trạng hôn nhân\n'
            if (not itern.identity and not itern.identity_2):
                error = error + u'- CMND\n'
            if itern.identity and not itern.place_cmnd:
                error = error + u'- nơi cấp CMND\n'
            if not itern.day_identity or not itern.month_identity or not itern.year_identity:
                error = error + u'- ngày cấp CMND\n'
            if not itern.hktt:
                error = error + u'- Địa chỉ HKTT\n'
            if not itern.last_education_from_month or not itern.last_education_from_year \
                or not itern.last_education_to_month or not itern.last_education_to_year or not itern.last_school_education_jp or not itern.last_school_education:
                error = error + u'- Trường học mới nhất\n'

            if not itern.time_start_at_pc_from_month or not itern.time_start_at_pc_from_year or not itern.total_time_at_pc_jp \
                or not itern.total_time_at_pc_vi:
                error = error + u'- thông tin làm việc tại Công ty PC2\n'

            if not itern.contact_person or not itern.contact_address or \
                    not itern.contact_relative or not itern.contact_phone:
                error = error + u'- người thân khi cần liên lạc\n'

            if error:
                raise ValidationError(u"Thiếu thông tin của %s:\n%s" % (itern.name,error))

        error2=""
        if not self.person_sign_proletter\
                or not self.position_person_sign:
            error2 = error2+u"- người ký thư tiến cử\n"
        if not self.day_create_letter_promotion or not self.month_create_letter_promotion or not self.year_create_letter_promotion:
            error2 = error2 + u"- ngày làm thư tiến cử\n"

        if not self.day_create_plan_training or not self.month_create_plan_training or not self.year_create_plan_training:
            error2 = error2 + u"- ngày lập kế hoạch đào tạo\n"
        if not self.day_start_training or not self.month_start_training or not self.year_start_training:
            error2 = error2 + u"- ngày bắt đầu khoá học\n"
        if not self.day_end_training or not self.month_end_training or not self.year_end_training:
            error2 = error2 + u"- ngày kết thúc khoá học\n"
        if not self.date_create_plan_training_report_customer or not self.month_create_plan_training_report_customer or not self.year_create_plan_training_report_customer:
            error2 = error2 + u"- ngày lập kế hoạch đào tạo báo cáo khách hàng\n"
        if not self.day_pay_finance1 or not self.month_pay_finance1 or not self.year_pay_finance1:
            error2 = error2 + u"- ngày nộp tài chính lần 1\n"
        if not self.day_pay_finance2 or not self.month_pay_finance2 or not self.year_pay_finance2:
            error2 = error2 + u"- ngày nộp tài chính lần 2\n"
        if not self.day_departure_doc or not self.month_departure_doc or not self.year_departure_doc:
            error2 = error2 + u"- ngày nộp xuất cảnh dự kiến\n"

        if not self.length_training or not self.hours_training:
            error2 = error2 + u"- thời gian đào tạo khoá học\n"
        if not self.training_center:
            error2 = error2 + u"- trung tâm đào tạo\n"
        if not self.guild:
            error2 = error2 + u"- nghiệp đoàn\n"
        if not self.enterprise_doc:
            error2 = error2 + u"- xí nghiệp\n"
        if not self.dispatchcom1:
            error2 = error2 + u"- pháp nhân\n"
        if not self.dispatchcom2:
            error2 = error2 + u"- công ty phái cử 2\n"

        if not self.name_working_department:
            error2 = error2 + u"- bộ phận TTS sẽ làm việc\n"
        if not self.job_en or not self.job_jp or not self.job_vi:
            error2 = error2 + u"- ngành nghề xin thư tiến cử\n"

        if error2:
            raise ValidationError(u"Thiếu thông tin bổ sung cho hồ sơ: \n%s"%error2)

        if not self.dispatchcom1.name_jp or not self.dispatchcom1.name_en or not self.dispatchcom1.name \
            or not self.dispatchcom1.director or not self.dispatchcom1.position_director or not self.dispatchcom1.position_director_vi \
            or not self.dispatchcom1.address_vi \
                or not self.dispatchcom1.address_en \
            or not self.dispatchcom1.phone_number or not self.dispatchcom1.date_create or not self.dispatchcom1.mission \
            or not self.dispatchcom1.capital or not self.dispatchcom1.revenue:
            raise ValidationError(u"Thiếu thông tin của pháp nhân")


        if not self.training_center.name_jp or not self.training_center.address_en \
                or not self.training_center.date_create or not self.training_center.phone_number \
            or not self.training_center.responsive_person or not self.training_center.mission:
            raise ValidationError(u"Thiếu thông tin của trung tâm đào tạo")


        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_extern_document?model=intern.invoice&id=%s&filename=hoso.zip' % (
                self.id),
            'target': 'self', }


    @api.multi
    def create_doc(self):
        _logger.info("CREATE DOC")

        if self.interns is None or len(self.interns) is 0:
            raise ValidationError("Không có thực tập sinh nào trong danh sách thi tuyển")


        for intern in self.interns:
            if intern.date_of_birth is None:
                raise ValidationError(u"Thiếu thông tin %s của %s"%(u'ngày sinh',intern.name))

            if not intern.name_in_japan:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Tên tiếng Nhật', intern.name))
            if not intern.gender:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Giới tính', intern.name))
            if not intern.blood_group:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Nhóm máu', intern.name))
            if intern.vision_left is None or intern.vision_right is None:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Thị lực', intern.name))
            if not intern.iq_percentage or intern.iq_percentage is None or intern.iq_percentage is 0:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Điểm IQ', intern.name))
            if intern.check_kureperin is None:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Điểm cộng dồn', intern.name))
            if not intern.marital_status:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Tình trạng hôn nhân', intern.name))
            if not intern.province or not intern.address:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Quê quán', intern.name))
            if not intern.certification:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Bằng cấp', intern.name))
            if intern.certification.id >2 and not intern.specialized:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Chuyên ngành', intern.name))

            if intern.height is None:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Chiều cao', intern.name))
            if intern.weight is None:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Cân nặng', intern.name))
            if not intern.favourite or not intern.strong or \
                    not intern.weak or not intern.family_income or not intern.motivation or \
                    not intern.income_after_three_year or not intern.job_after_return or \
                    not intern.prefer_object or not intern.memory or not intern.valuable:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'bổ sung tiếng Nhật', intern.name))

            if intern.educations is None or len(intern.educations) is 0:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Lý lịch Học tập', intern.name))
            if intern.family_members is None or len(intern.family_members) is 0:
                raise ValidationError(u"Thiếu thông tin %s của %s" % (u'Thành viên gia đình', intern.name))

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
            tmpaddress = intern.address
            if ',' in intern.address:
                tmp = intern.address.split(',')
                tmpaddress = tmp[len(tmp)-1].strip()

            context['dc'] = (intern_utils.no_accent_vietnamese(tmpaddress) + " - " + intern_utils.no_accent_vietnamese(intern.province.name)).upper()
            context['kc'] = intern.province.getDistanceString()
        if intern.phone_number:
            context['sdt'] = intern.phone_number
        if intern.height:
            context['cc'] = str(intern.height)
        if intern.weight:
            context['cn'] = str(intern.weight)
        if intern.vision_left and intern.vision_right:
            left = 1.5-(10.0-intern.vision_left)/10.0
            right = 1.5-(10.0-intern.vision_right)/10.0
            context['tl'] = "%.1f - %.1f"%(left,right)


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


        if intern.certification:
            if intern.certification.id == 1:
                intern.specialized = u'無し'
            elif intern.certification.id == 2:
                intern.specialized = u'無し'
        if intern.specialized:
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
        invoice = self.env['intern.invoice'].browse(int(id))
        if invoice:
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


    job = fields.Char("Ngành nghề")
    year_expire = fields.Integer("Thời hạn hợp đồng (năm)")
    salary_base = fields.Integer("Lương cơ bản")
    salary_real = fields.Integer("Lương thực lĩnh")
    subsidize_start_month = fields.Integer("Trợ cấp đầu tháng")
    number_man = fields.Integer("Số lượng nam")
    number_women = fields.Integer("Số lượng nữ")
    source_man = fields.Integer("Nguồn nam")
    source_women = fields.Integer("Nguồn nữ")

    age_from = fields.Integer("Tuổi từ")
    age_to = fields.Integer("Đến tuổi")
    certificate = fields.Many2one("intern.certification","Trình độ")
    marital = fields.Many2one("marital","Hôn nhân")
    vision = fields.Integer("Thị lực")
    physical = fields.Integer("Thể lực")
    preferred_hand = fields.Selection((('0', 'Tay phải'), ('1', 'Tay trái')), string="Tay thuận", default='0')
    height_man = fields.Integer("Chiều cao nam")
    height_women = fields.Integer("Chiều cao nữ")
    weight_man = fields.Integer("Cân nặng nam")
    weight_women = fields.Integer("Cân nặng nữ")
    smoking = fields.Boolean("Hút thuốc")

    job_description = fields.Char("Nội dung công việc")
    other_requirement = fields.Char("Tiêu chuẩn khác")

    note = fields.Char("Ghi chú")

    @api.model
    def _get_current_year(self):
        return str(datetime.now().year)

    #Thời hạn
    day_supply_form = fields.Char("Ngày", size=2)
    month_supply_form = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_supply_form = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    date_supply_form = fields.Char("Ngày cấp form", store=False, compute='_date_supply_form')

    @api.one
    @api.depends('day_supply_form', 'month_supply_form', 'year_supply_form')
    def _date_supply_form(self):
        if self.day_supply_form and self.month_supply_form and self.year_supply_form:
            self.date_supply_form = u"Ngày %s tháng %s năm %s" % (self.day_supply_form, self.month_supply_form, self.year_supply_form)
        elif self.month_supply_form and self.year_supply_form:
            self.date_supply_form = u"Tháng %s năm %s" % (
                                                 self.month_supply_form, self.year_supply_form)
        elif self.year_supply_form:
            self.date_supply_form = u'Năm %s'%self.year_supply_form
        else:
            self.date_supply_form = ""

    #
    day_check_form = fields.Char("Ngày", size=2)
    month_check_form = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_check_form = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    date_check_form = fields.Char("Ngày check form", store=False, compute='_date_check_form')

    @api.one
    @api.depends('day_check_form', 'month_check_form', 'year_check_form')
    def _date_check_form(self):
        if self.day_check_form and self.month_check_form and self.year_check_form:
            self.date_check_form = u"Ngày %s tháng %s năm %s" % (
                self.day_check_form, self.month_check_form, self.year_check_form)
        elif self.month_check_form and self.year_check_form:
            self.date_check_form = u"Tháng %s năm %s" % (
                self.month_check_form, self.year_check_form)
        elif self.year_check_form:
            self.date_check_form = u'Năm %s' % self.year_check_form
        else:
            self.date_check_form = ""

    #
    day_send_form = fields.Char("Ngày", size=2)
    month_send_form = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_send_form = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    date_send_form = fields.Char("Ngày gửi form", store=False, compute='_date_send_form')

    @api.one
    @api.depends('day_send_form', 'month_send_form', 'year_send_form')
    def _date_send_form(self):
        if self.day_send_form and self.month_send_form and self.year_send_form:
            self.date_send_form = u"Ngày %s tháng %s năm %s" % (
                self.day_send_form, self.month_send_form, self.year_send_form)
        elif self.month_send_form and self.year_send_form:
            self.date_send_form = u"Tháng %s năm %s" % (
                self.month_send_form, self.year_send_form)
        elif self.year_check_form:
            self.date_send_form = u'Năm %s' % self.year_send_form
        else:
            self.date_send_form = ""

    #
    day_exam = fields.Char("Ngày", size=2)
    month_exam = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_exam = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    date_exam = fields.Char("Ngày thi", store=False, compute='_date_exam')

    @api.one
    @api.depends('day_exam', 'month_exam', 'year_exam')
    def _date_exam(self):
        if self.day_exam and self.month_exam and self.year_exam:
            self.date_exam = u"Ngày %s tháng %s năm %s" % (
                self.day_exam, self.month_exam, self.year_exam)
        elif self.month_exam and self.year_exam:
            self.date_exam = u"Tháng %s năm %s" % (
                self.month_exam, self.year_exam)
        elif self.year_exam:
            self.date_exam = u'Năm %s' % self.year_exam
        else:
            self.date_exam = ""

    #
    day_departure = fields.Char("Ngày", size=2)
    month_departure = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_departure = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    date_departure = fields.Char("Ngày xuất cảnh Dự kiến", store=False, compute='_date_departure')

    @api.one
    @api.depends('day_departure', 'month_departure', 'year_departure')
    def _date_departure(self):
        if self.day_departure and self.month_departure and self.year_departure:
            self.date_departure = u"Ngày %s tháng %s năm %s" % (
                self.day_departure, self.month_departure, self.year_departure)
        elif self.month_departure and self.year_departure:
            self.date_departure = u"Tháng %s năm %s" % (
                self.month_departure, self.year_departure)
        elif self.year_departure:
            self.date_departure = u'Năm %s' % self.year_departure
        else:
            self.date_departure = ""

    room_responsive = fields.Char("Phòng NB phụ trách")

    status = fields.Selection([('0','Hoàn thành trúng tuyển'),('1','Hoàn thành xuất cảnh'),('2','Đã hủy TCLT-Visa-XC'),
                               ('3','Đang thực hiện'),('4','Đơn hàng hoãn - hủy thi tuyển'),('5','Đơn hàng hủy sau trung tuyển')],'Trạng thái đơn hàng')

    #
    day_finish = fields.Char("Ngày", size=2)
    month_finish = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_finish = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    date_finish = fields.Char("Ngày hoàn thành", store=False, compute='_date_finish')

    @api.one
    @api.depends('day_finish', 'month_finish', 'year_departure')
    def _date_finish(self):
        if self.day_finish and self.month_finish and self.year_finish:
            self.date_finish = u"Ngày %s tháng %s năm %s" % (
                self.day_finish, self.month_finish, self.year_finish)
        elif self.month_finish and self.year_departure:
            self.date_finish = u"Tháng %s năm %s" % (
                self.month_finish, self.year_finish)
        elif self.year_finish:
            self.date_finish = u'Năm %s' % self.year_finish
        else:
            self.date_finish = ""

    #
    day_cancel_tclt = fields.Char("Ngày", size=2)
    month_cancel_tclt = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_cancel_tclt = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    date_cancel_tclt = fields.Char("Ngày hủy TCLT", store=False, compute='_date_cancel_tclt')

    @api.one
    @api.depends('day_cancel_tclt', 'month_cancel_tclt', 'year_cancel_tclt')
    def _date_cancel_tclt(self):
        if self.day_cancel_tclt and self.month_cancel_tclt and self.year_cancel_tclt:
            self.date_cancel_tclt = u"Ngày %s tháng %s năm %s" % (
                self.day_cancel_tclt, self.month_cancel_tclt, self.year_cancel_tclt)
        elif self.month_cancel_tclt and self.year_departure:
            self.date_cancel_tclt = u"Tháng %s năm %s" % (
                self.month_cancel_tclt, self.year_cancel_tclt)
        elif self.year_cancel_tclt:
            self.date_cancel_tclt = u'Năm %s' % self.year_cancel_tclt
        else:
            self.date_cancel_tclt = ""

    #
    day_cancel_visa_xc = fields.Char("Ngày", size=2)
    month_cancel_visa_xc = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_cancel_visa_xc = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    date_cancel_visa_xc = fields.Char("Ngày hủy Visa-XC", store=False, compute='_date_cancel_visa_xc')

    @api.one
    @api.depends('day_cancel_visa_xc', 'month_cancel_visa_xc', 'year_cancel_visa_xc')
    def _date_cancel_visa_xc(self):
        if self.day_cancel_visa_xc and self.month_cancel_visa_xc and self.year_cancel_visa_xc:
            self.date_cancel_visa_xc = u"Ngày %s tháng %s năm %s" % (
                self.day_cancel_visa_xc, self.month_cancel_visa_xc, self.year_cancel_visa_xc)
        elif self.month_cancel_visa_xc and self.year_cancel_visa_xc:
            self.date_cancel_visa_xc = u"Tháng %s năm %s" % (
                self.month_cancel_visa_xc, self.year_cancel_visa_xc)
        elif self.year_cancel_tclt:
            self.date_cancel_visa_xc = u'Năm %s' % self.year_cancel_visa_xc
        else:
            self.date_cancel_visa_xc = ""


    #
    day_departure2 = fields.Char("Ngày", size=2)
    month_departure2 = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_departure2 = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    date_departure2 = fields.Char("Ngày xuất cảnh", store=False, compute='_date_departure2')

    @api.one
    @api.depends('day_departure2', 'month_departure2', 'year_departure2')
    def _date_departure2(self):
        if self.day_departure2 and self.month_departure2 and self.year_departure2:
            self.date_departure2 = u"Ngày %s tháng %s năm %s" % (
                self.day_departure2, self.month_departure2, self.year_departure2)
        elif self.month_departure2 and self.year_departure2:
            self.date_departure2 = u"Tháng %s năm %s" % (
                self.month_departure2, self.year_departure2)
        elif self.year_departure2:
            self.date_departure2 = u'Năm %s' % self.year_departure2
        else:
            self.date_departure2 = ""


    reason_cancel_tclt_visa_xc =fields.Char("Lý do đơn hàng bị hủy TCLT - Visa - XC")


    # create_date_only = fields.Char("Ngày tạo",store=False,compute='_get_create_date')

    # @api.one
    # def _get_create_date(self):
    #     if self.create_date is not None:
    #         create_date_only = self.create_date[10:]





    #Thong tin bo sung cho ho so noi

    day_create_letter_promotion = fields.Char("Ngày", size=2)
    month_create_letter_promotion = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_create_letter_promotion = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())
    date_create_letter_promotion = fields.Char("Ngày làm thư tiến cử", store=False, compute='_date_create_letter_pro')

    @api.multi
    @api.depends('day_create_letter_promotion', 'month_create_letter_promotion', 'year_create_letter_promotion')
    def _date_create_letter_pro(self):

        for rec in self:
            if rec.day_create_letter_promotion and rec.month_create_letter_promotion and rec.year_create_letter_promotion:
                rec.date_create_letter_promotion = u"Ngày %s tháng %s năm %s" % (
                    rec.day_create_letter_promotion, rec.month_create_letter_promotion, rec.year_create_letter_promotion)
            elif rec.month_create_letter_promotion and rec.year_create_letter_promotion:
                rec.date_create_letter_promotion = u"Tháng %s năm %s" % (
                    rec.month_create_letter_promotion, rec.year_create_letter_promotion)
            elif rec.year_create_letter_promotion:
                rec.date_create_letter_promotion = u'Năm %s' % rec.year_create_letter_promotion
            else:
                rec.date_create_letter_promotion = ""


    day_create_plan_training = fields.Char("Ngày", size=2)
    month_create_plan_training = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_create_plan_training = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())
    date_create_plan_training = fields.Char("Ngày lập kế hoạch đào tạo theo ủy thác(Trước ngày bắt đầu ít nhất 1 ngày, chú ý Chủ Nhật)", store=False, compute='_date_create_plan_training')


    @api.multi
    @api.depends('day_create_plan_training', 'month_create_plan_training', 'year_create_plan_training')
    def _date_create_plan_training(self):
        for rec in self:
            if rec.day_create_plan_training and rec.month_create_plan_training and rec.year_create_plan_training:
                rec.date_create_plan_training = u"Ngày %s tháng %s năm %s" % (
                    rec.day_create_plan_training, rec.month_create_plan_training, rec.year_create_plan_training)
            elif rec.month_create_plan_training and rec.year_create_plan_training:
                rec.date_create_plan_training = u"Tháng %s năm %s" % (
                    rec.month_create_plan_training, rec.year_create_plan_training)
            elif rec.year_create_plan_training:
                rec.date_create_plan_training = u'Năm %s' % rec.year_create_plan_training
            else:
                rec.date_create_plan_training = ""

    day_start_training = fields.Char("Ngày", size=2)
    month_start_training = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_start_training = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    date_start_training = fields.Char("Ngày bắt đầu khóa học chú ý Chủ Nhật(Trước ngày bắt đầu 1 tháng)", store=False, compute='_date_start_training')


    @api.multi
    @api.depends('day_start_training', 'month_start_training', 'year_start_training')
    def _date_start_training(self):
        for rec in self:
            if rec.day_start_training and rec.month_start_training and rec.year_start_training:
                rec.date_start_training = u"Ngày %s tháng %s năm %s" % (
                    rec.day_start_training, rec.month_start_training, rec.year_start_training)
            elif rec.month_start_training and rec.year_start_training:
                rec.date_start_training = u"Tháng %s năm %s" % (
                    rec.month_start_training, rec.year_start_training)
            elif rec.year_start_training:
                rec.date_start_training = u'Năm %s' % rec.year_start_training
            else:
                rec.date_start_training = ""

    day_end_training = fields.Char("Ngày", size=2)
    month_end_training = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_end_training = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())
    date_end_training = fields.Char("Ngày kết thúc khóa học(chú ý Chủ Nhật) Tính từ thời điểm làm hồ sơ sau khoảng 10 ngày", store=False, compute='_date_end_training')



    @api.multi
    @api.depends('day_end_training', 'month_end_training', 'year_end_training')
    def _date_end_training(self):
        for rec in self:
            if rec.day_end_training and rec.month_end_training and rec.year_end_training:
                rec.date_end_training = u"Ngày %s tháng %s năm %s" % (
                    rec.day_end_training, rec.month_end_training, rec.year_end_training)
            elif rec.month_end_training and rec.year_end_training:
                rec.date_end_training = u"Tháng %s năm %s" % (
                    rec.month_end_training, rec.year_end_training)
            elif rec.year_end_training:
                rec.date_end_training = u'Năm %s' % rec.year_end_training
            else:
                rec.date_end_training = ""

    day_create_plan_training_report_customer = fields.Char("Ngày", size=2)
    month_create_plan_training_report_customer = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_create_plan_training_report_customer = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())
    date_create_plan_training_report_customer = fields.Char("Ngày lập kế hoạch đào tạo BÁO CÁO KHÁCH HÀNG trước ngày bắt đầu ít nhất 1 ngày chú ý CHỦ NHẬT", store=False, compute='_date_create_plan_training_report_customer')


    @api.multi
    @api.depends('day_create_plan_training_report_customer', 'month_create_plan_training_report_customer', 'year_create_plan_training_report_customer')
    def _date_create_plan_training_report_customer(self):
        for rec in self:
            if rec.day_create_plan_training_report_customer and rec.month_create_plan_training_report_customer and rec.year_create_plan_training_report_customer:
                rec.date_create_plan_training_report_customer = u"Ngày %s tháng %s năm %s" % (
                    rec.day_create_plan_training_report_customer, rec.month_create_plan_training_report_customer, rec.year_create_plan_training_report_customer)
            elif rec.month_create_plan_training_report_customer and rec.year_create_plan_training_report_customer:
                rec.date_create_plan_training_report_customer = u"Tháng %s năm %s" % (
                    rec.month_create_plan_training_report_customer, rec.year_create_plan_training_report_customer)
            elif rec.year_create_plan_training_report_customer:
                rec.date_create_plan_training_report_customer = u'Năm %s' % rec.year_create_plan_training_report_customer
            else:
                rec.date_create_plan_training_report_customer = ""

    day_pay_finance1 = fields.Char("Ngày", size=2)
    month_pay_finance1 = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_pay_finance1 = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())
    date_pay_finance1 = fields.Char("Ngày nộp tài chính đợt 1 (Sau ngày trúng tuyển 7 ngày)", store=False, compute='_date_pay_finance1')



    @api.multi
    @api.depends('day_pay_finance1', 'month_pay_finance1',
                 'year_pay_finance1')
    def _date_pay_finance1(self):
        for rec in self:
            if rec.day_pay_finance1 and rec.month_pay_finance1 and rec.year_pay_finance1:
                rec.date_pay_finance1 = u"Ngày %s tháng %s năm %s" % (
                    rec.day_pay_finance1, rec.month_pay_finance1,
                    rec.year_pay_finance1)
            elif rec.month_pay_finance1 and rec.year_pay_finance1:
                rec.date_pay_finance1 = u"Tháng %s năm %s" % (
                    rec.month_pay_finance1, rec.year_pay_finance1)
            elif rec.year_pay_finance1:
                rec.date_pay_finance1 = u'Năm %s' % rec.year_pay_finance1
            else:
                rec.date_pay_finance1 = ""

    day_pay_finance2 = fields.Char("Ngày", size=2)
    month_pay_finance2 = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_pay_finance2 = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())
    date_pay_finance2 = fields.Char("Ngày nộp tài chính đợt 2 (Trước ngày dự kiến xuất cảnh 10 ngày)", store=False, compute='_date_pay_finance2')



    @api.multi
    @api.depends('day_pay_finance2', 'month_pay_finance2',
                 'year_pay_finance2')
    def _date_pay_finance2(self):
        for rec in self:
            if rec.day_pay_finance2 and rec.month_pay_finance2 and rec.year_pay_finance2:
                rec.date_pay_finance2 = u"Ngày %s tháng %s năm %s" % (
                    rec.day_pay_finance2, rec.month_pay_finance2,
                    rec.year_pay_finance2)
            elif rec.month_pay_finance2 and rec.year_pay_finance2:
                rec.date_pay_finance2 = u"Tháng %s năm %s" % (
                    rec.month_pay_finance2, rec.year_pay_finance2)
            elif rec.year_pay_finance2:
                rec.date_pay_finance2 = u'Năm %s' % rec.year_pay_finance2
            else:
                rec.date_pay_finance2 = ""



    length_training = fields.Char("Thời gian đào tạo khóa học (Chữ Hán)")
    hours_training = fields.Integer("Tổng số thời gian đào tạo (số giờ học)")

    training_center = fields.Many2one('trainingcenter','Trung tâm đào tạo')
    guild = fields.Many2one('intern.guild','Nghiệp đoàn')

    enterprise_doc = fields.Many2one('intern.enterprise','Xí nghiệp')

    dispatchcom2 = fields.Many2one('dispatchcom2','Công ty phái cử thứ 2')
    dispatchcom1 = fields.Many2one('dispatchcom1','Pháp nhân')



    name_working_department = fields.Char("Tên bộ phận TTS sẽ làm việc trong xí nghiệp (có trong hợp đồng lương) - Tiếng Nhật ")

    job_en = fields.Char("Ngành nghề xin thư tiến cử lấy từ hợp đồng lương (Tiếng Anh)")
    job_jp = fields.Char("Ngành nghề xin thư tiến cử lấy từ hợp đồng lương (Tiếng Nhật)")
    job_vi = fields.Char("Ngành nghề xin thư tiến cử lấy từ hợp đồng lương (Tiếng Việt)")

    day_departure_doc = fields.Char("Ngày", size=2)
    month_departure_doc = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_departure_doc = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())

    date_departure_doc = fields.Char("Ngày xuất cảnh Dự kiến", store=False, compute='_date_departure_doc')


    @api.multi
    @api.depends('day_departure_doc', 'month_departure_doc', 'year_departure_doc')
    def _date_departure_doc(self):
        for rec in self:
            if rec.day_departure_doc and rec.month_departure_doc and rec.year_departure_doc:
                rec.date_departure_doc = u"Ngày %s tháng %s năm %s" % (
                    rec.day_departure_doc, rec.month_departure_doc, rec.year_departure_doc)
            elif rec.month_departure_doc and rec.year_departure_doc:
                rec.date_departure_doc = u"Tháng %s năm %s" % (
                    rec.month_departure_doc, rec.year_departure_doc)
            elif rec.year_departure_doc:
                rec.date_departure_doc = u'Năm %s' % rec.year_departure_doc
            else:
                rec.date_departure_doc = ""

    person_sign_proletter = fields.Char("Tên người ký thư tiến cử (kiểm tra thường xuyên tránh sai)",default=u"Vũ Trường Giang")
    position_person_sign = fields.Char("Chức danh người ký thư tiến cử - Tiếng Anh",default=u'Head of Division for Japan - Europe - Southeast Asia')
    position_person_sign_jp= fields.Char("Chức danh người ký thư tiến cử - Tiếng Nhật",default=u'日本ヨーロッパー東南アジア部長')
    developing_employee = fields.Char("Cán bộ PTTT")

    back_to_pc2 = fields.Boolean('Sau khi về nước sẽ quay lại Cty PC2 ')

    day_sign_proletter = fields.Char("Ngày", size=2)
    month_sign_proletter = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                           ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                           ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")

    year_sign_proletter = fields.Char("Năm", size=4, default=lambda self: self._get_current_year())
    date_sign_proletter = fields.Char("Ngày ký hợp đồng phái cử", store=False,
                                    compute='_date_sign_proletter')     #a122

    @api.multi
    @api.depends('day_sign_proletter', 'month_sign_proletter',
                 'year_sign_proletter')
    def _date_sign_proletter(self):
        for rec in self:
            if rec.day_sign_proletter and rec.month_sign_proletter and rec.year_sign_proletter:
                rec.date_sign_proletter = u"Ngày %s tháng %s năm %s" % (
                    rec.day_sign_proletter, rec.month_sign_proletter,
                    rec.year_sign_proletter)
            elif rec.month_sign_proletter and rec.year_sign_proletter:
                rec.date_sign_proletter = u"Tháng %s năm %s" % (
                    rec.month_sign_proletter, rec.year_sign_proletter)
            elif rec.year_pay_finance2:
                rec.date_sign_proletter = u'Năm %s' % rec.year_sign_proletter
            else:
                rec.date_sign_proletter = ""


    def create_doc_1_3(self, intern, index):
        docs = self.env['intern.document'].search([('name', '=', "Doc1-3")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}

             #ovan 3 la Nu, 1 la nam, 2 la ko, 5 la co

            if intern.gender == 'nam':
                tpl.remove_shape(u'id="1" name="Oval 1"')

            else:
                tpl.remove_shape(u'id="5" name="Oval 5"')

            if intern.marital_status.id is not 2:
                tpl.remove_shape(u'id="2" name="Oval 2"')
            else:
                tpl.remove_shape(u'id="6" name="Oval 6"')

            context['a3'] = intern_utils.no_accent_vietnamese(intern.name).upper()
            context['a5'] = intern.name_in_japan.replace(u'・', '  ')
            context['a7'] = intern_utils.date_time_in_jp(intern.day,intern.month,intern.year)
            context['a8'] = intern_utils.date_time_in_vn(intern.day,intern.month,intern.year)
            context['a11'] = str(intern_utils.get_age_jp(intern.day, intern.month,intern.year))
            if intern.hktt:
                context['a15_1'] = intern_utils.no_accent_vietnamese(intern.hktt).upper()
                context['a15'] = intern.hktt.upper()

            context['a21'] = u'%s ~ %s'%(intern_utils.date_time_in_vn2(intern.last_education_from_month,intern.last_education_from_year),
                                        intern_utils.date_time_in_vn2( intern.last_education_to_month,
                                                                     intern.last_education_to_year))
            context['a21_1'] = u'%s ～ %s'%(intern_utils.date_time_in_jp(None,intern.last_education_from_month,intern.last_education_from_year),
                                          intern_utils.date_time_in_jp(None, intern.last_education_to_month,
                                                                       intern.last_education_to_year))
            context['a22'] = intern.last_school_education_jp
            context['a23'] = intern.last_school_education

            if intern.last_education_from_month2 and intern.last_education_from_year2 and \
                    intern.last_education_to_month2 and intern.last_education_to_year2 \
                     and intern.last_school_education_jp2 and intern.last_school_education2:
                context['b21'] = u'%s ~ %s' % (
                intern_utils.date_time_in_vn2( intern.last_education_from_month2, intern.last_education_from_year2),
                intern_utils.date_time_in_vn2( intern.last_education_to_month2,
                                             intern.last_education_to_year2))
                context['b21_1'] = u'%s ～ %s' % (
                intern_utils.date_time_in_jp(None, intern.last_education_from_month2, intern.last_education_from_year2),
                intern_utils.date_time_in_jp(None, intern.last_education_to_month2,
                                             intern.last_education_to_year2))
                context['b22'] = intern.last_school_education_jp2
                context['b23'] = intern.last_school_education2

            table_jobs = []
            for i in range(0,4):
                if i == 0:
                    info = {}
                    if intern.time_employee and intern.job_employee_jp and intern.job_employee_vi:
                        info['a25'] = u'%s ~ %s' % (
                        intern_utils.date_time_in_vn2(intern.time_employee_from_month, intern.time_employee_from_year),
                        intern_utils.date_time_in_vn2(intern.time_employee_to_month,
                                                     intern.time_employee_to_year))
                        info['a25_1'] = intern.time_employee
                        info['a26'] = intern.job_employee_jp
                        info['a27'] = intern.job_employee_vi
                        table_jobs.append(info)
                    else:
                        break
                if i == 1:
                    info = {}
                    if intern.time_employee2 and intern.job_employee2_jp and intern.job_employee2_vi:
                        info['a25'] = u'%s ~ %s' % (
                        intern_utils.date_time_in_vn2(intern.time_employee2_from_month, intern.time_employee2_from_year),
                        intern_utils.date_time_in_vn2(intern.time_employee2_to_month,
                                                     intern.time_employee2_to_year))
                        info['a25_1'] = intern.time_employee2
                        info['a26'] = intern.job_employee2_jp
                        info['a27'] = intern.job_employee2_vi
                        table_jobs.append(info)
                    else:
                        break
                if i == 2:
                    info = {}
                    if intern.time_employee3 and intern.job_employee3_jp and intern.job_employee3_vi:
                        info['a25'] = u'%s ~ %s' % (
                        intern_utils.date_time_in_vn2(intern.time_employee3_from_month, intern.time_employee3_from_year),
                        intern_utils.date_time_in_vn2(intern.time_employee3_to_month,
                                                     intern.time_employee3_to_year))
                        info['a25_1'] = intern.time_employee3
                        info['a26'] = intern.job_employee3_jp
                        info['a27'] = intern.job_employee3_vi
                        table_jobs.append(info)
                    else:
                        break
                if i == 3:
                    info = {}
                    if intern.time_employee4 and intern.job_employee4_jp and intern.job_employee4_vi:
                        info['a25'] = u'%s ~ %s' % (
                        intern_utils.date_time_in_vn2(intern.time_employee4_from_month, intern.time_employee4_from_year),
                        intern_utils.date_time_in_vn2(intern.time_employee4_to_month,
                                                     intern.time_employee4_to_year))
                        info['a25_1'] = intern.time_employee4
                        info['a26'] = intern.job_employee4_jp
                        info['a27'] = intern.job_employee4_vi
                        table_jobs.append(info)
                    else:
                        break

                if i == 4:
                    info = {}
                    if intern.time_employee5 and intern.job_employee5_jp and intern.job_employee5_vi:
                        info['a25'] = u'%s ~ %s' % (
                        intern_utils.date_time_in_vn2(intern.time_employee5_from_month, intern.time_employee5_from_year),
                        intern_utils.date_time_in_vn2(intern.time_employee5_to_month,
                                                     intern.time_employee5_to_year))
                        info['a25_1'] = intern.time_employee5
                        info['a26'] = intern.job_employee5_jp
                        info['a27'] = intern.job_employee5_vi
                        table_jobs.append(info)
                    else:
                        break


            info = {}

            info['a25'] = u'%s ~ Hiện nay' % (
                                intern_utils.date_time_in_vn2(intern.time_start_at_pc_from_month, intern.time_start_at_pc_from_year))
            info['a25_1'] = intern.time_start_at_pc

            info['a26'] = "%s (%s)" %(self.dispatchcom2.name,self.job_jp)
            info['a27'] = "%s (%s)" %(self.dispatchcom2.name_vn,self.job_vi)
            table_jobs.append(info)
            if len(table_jobs) == 1:
                table_jobs.append({})

            context['tbl_jobs'] = table_jobs


            context['a38'] = intern.total_time_at_pc_jp
            context['a39'] = intern.total_time_at_pc_vi


            context['a40'] = intern_utils.date_time_in_jp(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)

            context['a42'] = intern_utils.date_time_in_vn(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)




            context['a84'] = self.job_jp
            context['a85'] = self.job_vi


            tpl.render(context)


            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile

    def create_doc_1_10(self, intern):
        docs = self.env['intern.document'].search([('name', '=', "Doc1-10")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}
            context['a3'] = intern_utils.no_accent_vietnamese(intern.name).upper()
            context['a59'] = self.guild.name_in_jp
            context['a74'] = self.enterprise_doc.name_jp
            context['a40'] = intern_utils.date_time_in_jp(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)
            context['a102'] = self.dispatchcom1.name_en.upper()
            context['a105'] = intern_utils.no_accent_vietnamese(self.dispatchcom1.director).upper()

            tpl.render(context)

            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile

    def create_doc_1_20(self):
        if self.back_to_pc2:
            docs = self.env['intern.document'].search([('name', '=', "Doc1-20")], limit=1)
        else:
            docs = self.env['intern.document'].search([('name', '=', "Doc1-20-TH2")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}

            context['a40'] = intern_utils.date_time_in_jp(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)
            context['a42'] = intern_utils.date_time_in_vn(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)

            context['a84'] = self.job_jp
            context['a85'] = self.job_vi.lower()
            tpl.render(context)

            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile

    def create_doc_1_21(self, intern):
        if self.year_expire == 3:
            docs = self.env['intern.document'].search([('name', '=', "Doc1-21")], limit=1)
        else:
            docs = self.env['intern.document'].search([('name', '=', "Doc1-21-1")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}

            context['a59'] = self.guild.name_in_jp
            context['a60'] = self.guild.name_in_en
            context['a74'] = self.enterprise_doc.name_jp
            context['a75'] = self.enterprise_doc.name_romaji
            context['a3'] = intern_utils.no_accent_vietnamese(intern.name).upper()
            context['a5'] = intern.name_in_japan.replace(u'・', '  ')
            context['a47'] = intern_utils.date_time_in_jp(self.day_pay_finance1,self.month_pay_finance1,self.year_pay_finance1)
            context['a48'] = self.date_pay_finance1
            context['a49'] = intern_utils.date_time_in_jp(self.day_pay_finance2, self.month_pay_finance2,
                                                          self.year_pay_finance2)
            context['a50'] = self.date_pay_finance2

            context['a40'] = intern_utils.date_time_in_jp(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)
            context['a42'] = intern_utils.date_time_in_vn(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)

            context['a102'] = self.dispatchcom1.name_en.upper()
            context['a104'] = self.dispatchcom1.name.upper()
            context['a105'] = intern_utils.no_accent_vietnamese(self.dispatchcom1.director).upper()
            context['a105_1'] = self.dispatchcom1.director.upper()
            context['a106'] = self.dispatchcom1.position_director
            context['a123'] = self.dispatchcom1.position_director_vi


            tpl.render(context)

            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile

    def create_doc_1_28(self, intern):
        if self.back_to_pc2:
            docs = self.env['intern.document'].search([('name', '=', "Doc1-28")], limit=1)
        else:
            docs = self.env['intern.document'].search([('name', '=', "Doc1-28-TH2")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}

            context['a3'] = intern_utils.no_accent_vietnamese(intern.name).upper()
            context['a5'] = intern.name_in_japan.replace(u'・', '  ')
            context['a84'] = self.job_jp
            context['a82'] = self.name_working_department
            context['a92'] = self.dispatchcom2.name
            context['a95'] = self.dispatchcom2.director.upper()
            context['a40'] = intern_utils.date_time_in_jp(self.day_create_letter_promotion,self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)

            if self.back_to_pc2:
                context['a92'] = self.dispatchcom2.name

            tpl.render(context)

            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile




    def create_hdtn(self, intern):
        docs = self.env['intern.document'].search([('name', '=', "DocHDTN")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}

            context['a3'] = intern_utils.no_accent_vietnamese(intern.name).upper()
            context['a7'] = intern_utils.date_time_in_jp(intern.day,intern.month,intern.year)

            context['a10'] = intern_utils.date_time_in_jp(intern.day_identity,intern.month_identity,intern.year_identity)
            context['a15'] = intern_utils.no_accent_vietnamese(intern.hktt).upper()
            if intern.identity:
                context['a16'] = u'%s省公安'%(intern_utils.no_accent_vietnamese(intern.place_cmnd.name))
                context['a9'] = intern.identity
            else:
                context['a9'] = intern.identity_2
                context['a16'] = u'警察局局長'

            context['a17'] = intern_utils.no_accent_vietnamese(intern.contact_person).upper()
            context['a18'] = intern_utils.no_accent_vietnamese(intern.contact_address).upper()
            context['a19'] = intern.contact_relative.relation_jp
            context['a20'] = intern.contact_phone
            context['a59'] = self.guild.name_in_jp
            context['a70'] = intern_utils.date_time_in_jp(self.guild.day_sign,self.guild.month_sign,self.guild.year_sign)
            context['a73'] = str("{:,}".format(self.guild.subsidize_start_month))
            context['a74'] = self.enterprise_doc.name_jp
            context['a76'] = self.enterprise_doc.address_jp
            context['a77'] = self.enterprise_doc.phone_number
            context['a84'] = self.job_jp
            context['a86'] = self.year_expire

            context['a122'] = intern_utils.date_time_in_jp_missing(self.day_sign_proletter,self.month_sign_proletter,self.year_sign_proletter)
            context['a122_3'] = self.year_sign_proletter

            context['a102'] = self.dispatchcom1.name_en.upper()
            context['a105'] = intern_utils.no_accent_vietnamese(self.dispatchcom1.director).upper()
            context['a106'] = self.dispatchcom1.position_director
            context['a112'] = self.dispatchcom1.address_en
            context['a110'] = self.dispatchcom1.phone_number
            if self.dispatchcom1.fax_number:
                context['a111'] = self.dispatchcom1.fax_number

            tpl.render(context)

            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile

    def create_hdtv(self, intern):
        docs = self.env['intern.document'].search([('name', '=', "DocHDTV")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}

            context['a1'] = intern.name.upper()
            context['a6'] = intern_utils.date_time_in_en(intern.day, intern.month, intern.year)

            context['a10_1'] = intern_utils.date_time_in_en(intern.day_identity, intern.month_identity,
                                                          intern.year_identity)
            context['a15_1'] = intern.hktt
            if intern.identity:
                context['a16_1'] = u'Công An %s' %(intern.place_cmnd.name)
                context['a9'] = intern.identity
            else:
                context['a9'] = intern.identity_2
                context['a16_1'] = u'Cục trưởng Cục cảnh sát'

            context['a17_1'] = intern.contact_person
            context['a18_1'] = intern.contact_address
            context['a19_1'] = intern.contact_relative.relation
            context['a20'] = intern.contact_phone
            context['a60_2'] = self.guild.name_in_en.upper().replace('KYODO KUMIAI','')
            context['a71'] = intern_utils.date_time_in_en(self.guild.day_sign, self.guild.month_sign,
                                                          self.guild.year_sign)
            context['a73'] = intern_utils.format_number_in_vn(str(self.guild.subsidize_start_month))
            context['a75'] = self.enterprise_doc.name_romaji.upper()
            context['a79'] = self.enterprise_doc.address_romoji
            context['a77'] = self.enterprise_doc.phone_number
            context['a85'] = self.job_vi
            context['a86'] = self.year_expire

            context['a122'] = intern_utils.date_time_in_en_missing(self.day_sign_proletter, self.month_sign_proletter,
                                                           self.year_sign_proletter)
            context['a122_3'] = self.year_sign_proletter
            context['a104'] = self.dispatchcom1.name
            context['a105'] = self.dispatchcom1.director
            context['a123'] = self.dispatchcom1.position_director_vi
            context['a124'] = self.dispatchcom1.address_vi
            context['a110'] = self.dispatchcom1.phone_number
            if self.dispatchcom1.fax_number:
                context['a111'] = self.dispatchcom1.fax_number

            tpl.render(context)

            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile


    def create_doc_1_29(self):
        docs = self.env['intern.document'].search([('name', '=', "Doc1-29")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}

            table_interns = []
            for i, intern in enumerate(self.interns_pass):
                info = {}
                info['stt'] = str(i + 1)
                info['htk'] = intern_utils.no_accent_vietnamese(intern.name).upper()
                info['xc'] = intern_utils.date_time_in_jp(self.day_departure_doc,self.month_departure_doc,self.year_departure_doc)

                table_interns.append(info)


            context['a43'] = intern_utils.date_time_in_jp(self.day_create_plan_training,self.month_create_plan_training,self.year_create_plan_training)
            context['a44'] = intern_utils.date_time_in_jp(self.day_start_training,self.month_start_training,self.year_start_training)
            context['a45'] = intern_utils.date_time_in_jp(self.day_end_training,self.month_end_training,self.year_end_training)
            context['a53'] = self.training_center.name_jp
            # context['a54'] = self.training_center.address_jp
            context['a54'] = self.training_center.address_en
            context['a59'] = self.guild.name_in_jp
            context['a61'] = self.guild.address_in_jp
            context['a66'] = self.guild.position_of_responsive_jp
            context['a68'] = self.guild.name_of_responsive_jp

            context['tbl_intern'] = table_interns

            tpl.render(context)

            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile

    def create_master(self):
        docs = self.env['intern.document'].search([('name', '=', "DocMaster")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}
            intern = self.interns_pass[0]
            context['a1'] = intern.name.upper()
            context['a2'] = intern.name.upper()
            context['a3'] = intern_utils.no_accent_vietnamese(intern.name).upper()
            context['a4'] = str(len(self.interns_pass)-1)
            context['a5'] = intern.name_in_japan.replace(u'・', ' ')
            context['a6'] = intern_utils.date_time_in_en(intern.day, intern.month, intern.year)
            context['a7'] = intern_utils.date_time_in_jp(intern.day,intern.month,intern.year)
            context['a8'] = intern_utils.date_time_in_vn(intern.day, intern.month, intern.year)
            if intern.identity:
                context['a9'] = intern.identity
                context['a16'] = u'%s省公安' % (intern_utils.no_accent_vietnamese(intern.place_cmnd.name))
            else:
                context['a9'] = intern.identity_2
                context['a16'] = u'警察局局長'
            context['a10'] = intern_utils.date_time_in_jp(intern.day_identity, intern.month_identity,
                                                          intern.year_identity)
            context['a11'] = str(intern_utils.get_age_jp(intern.day,intern.month,intern.year))
            if intern.gender == 'nam':
                context['a12'] = u'男'
                context['a13'] = u'MALE'
            else:
                context['a12'] = u'女'
                context['a13'] = u'FEMALE'
            if intern.marital_status.id is not 2:
                context['a14'] = u'無'
            else:
                context['a14'] = u'有'

            if intern.hktt:
                context['a15'] = intern_utils.no_accent_vietnamese(intern.hktt).upper()

            context['a17'] = intern_utils.no_accent_vietnamese(intern.contact_person).upper()
            context['a18'] = intern_utils.no_accent_vietnamese(intern.contact_address).upper()
            context['a19'] = intern.contact_relative.relation_jp
            context['a20'] = intern.contact_phone
            context['a21'] = intern.last_time_education
            context['a22'] = intern.last_school_education_jp
            context['a23'] = intern.last_school_education
            context['a24'] = intern.last_time_education
            context['a25'] = intern.time_employee
            context['a26'] = intern.job_employee_jp
            context['a27'] = intern.job_employee_vi

            if intern.time_employee2 and intern.job_employee2_jp and intern.job_employee2_vi:
                context['a28'] = intern.time_employee2
                context['a29'] = intern.job_employee2_jp
                context['a30'] = intern.job_employee2_vi

            if intern.time_employee3 and intern.job_employee3_jp and intern.job_employee3_vi:
                context['a31'] = intern.time_employee3
                context['a32'] = intern.job_employee3_jp
                context['a33'] = intern.job_employee3_vi

            context['a34'] = intern_utils.date_time_in_jp(self.dispatchcom2.day_create, self.dispatchcom2.month_create,
                                                          self.dispatchcom2.year_create)
            context['a35'] = intern.time_start_at_pc
            context['a36'] = "%s (%s)" % (self.dispatchcom2.name, self.job_jp)
            context['a37'] = "%s (%s)" % (self.dispatchcom2.name_vn, self.job_vi)
            context['a38'] = intern.total_time_at_pc_jp
            context['a39'] = intern.total_time_at_pc_vi

            context['a40'] = intern_utils.date_time_in_jp(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)
            context['a41'] = intern_utils.date_time_in_en(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)

            context['a42'] = intern_utils.date_time_in_vn(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)

            context['a43'] = intern_utils.date_time_in_jp(self.day_create_plan_training,
                                                          self.month_create_plan_training,
                                                          self.year_create_plan_training)
            context['a44'] = intern_utils.date_time_in_jp(self.day_start_training, self.month_start_training,
                                                          self.year_start_training)
            context['a45'] = intern_utils.date_time_in_jp(self.day_end_training, self.month_end_training,
                                                          self.year_end_training)

            context['a46'] = intern_utils.date_time_in_jp(self.day_create_plan_training_report_customer,self.month_create_plan_training_report_customer,self.year_create_plan_training_report_customer)
            context['a47'] = intern_utils.date_time_in_jp(self.day_pay_finance1, self.month_pay_finance1,
                                                          self.year_pay_finance1)
            context['a48'] = self.date_pay_finance1
            context['a49'] = intern_utils.date_time_in_jp(self.day_pay_finance2, self.month_pay_finance2,
                                                          self.year_pay_finance2)
            context['a50'] = self.date_pay_finance2
            context['a51'] = self.length_training
            context['a52'] = str(self.hours_training)
            context['a53'] = self.training_center.name_jp
            # context['a54'] = self.training_center.address_jp
            context['a55'] = intern_utils.date_time_in_jp(self.training_center.day_create,self.training_center.month_create,self.training_center.year_create)
            context['a56'] = self.training_center.phone_number
            context['a57'] = intern_utils.no_accent_vietnamese(self.training_center.responsive_person)
            context['a58'] = self.guild.name_acronym
            context['a59'] = self.guild.name_in_jp
            context['a60'] = self.guild.name_in_en.upper()
            context['a61'] = self.guild.address_in_jp
            context['a62'] = self.guild.address_in_romaji
            context['a63'] = self.guild.post_code
            context['a64'] = self.guild.phone_number
            if self.guild.fax_number:
                context['a65'] = self.guild.fax_number
            context['a66'] = self.guild.position_of_responsive_jp
            context['a67'] = self.guild.position_of_responsive_vi
            context['a68'] = self.guild.name_of_responsive_jp
            context['a69'] = self.guild.name_of_responsive_romaji
            context['a70'] = intern_utils.date_time_in_jp(self.guild.day_sign, self.guild.month_sign,
                                                          self.guild.year_sign)
            context['a71'] = intern_utils.date_time_in_en(self.guild.day_sign, self.guild.month_sign,
                                                          self.guild.year_sign)
            context['a72'] = self.guild.fee_training_nd_to_pc
            context['a73'] = str(self.guild.subsidize_start_month)
            context['a74'] = self.enterprise_doc.name_jp
            context['a75'] = self.enterprise_doc.name_romaji
            context['a76'] = self.enterprise_doc.address_jp
            context['a77'] = self.enterprise_doc.phone_number
            if self.enterprise_doc.fax_number:
                context['a78'] = self.enterprise_doc.fax_number
            context['a79'] = self.enterprise_doc.address_romoji
            context['a80'] = self.enterprise_doc.name_of_responsive_jp
            context['a81'] = self.enterprise_doc.name_of_responsive_en
            context['a82'] = self.name_working_department
            context['a83'] = self.job_en
            context['a84'] = self.job_jp
            context['a85'] = self.job_vi
            context['a86'] = self.year_expire
            context['a87'] = intern_utils.date_time_in_jp(self.day_departure_doc,self.month_departure_doc,self.year_departure_doc)
            context['a88'] = self.year_departure_doc
            context['a89'] = self.month_departure_doc
            context['a90'] = self.person_sign_proletter
            context['a91'] = self.position_person_sign
            context['a92'] = self.dispatchcom2.name
            if self.dispatchcom2.address:
                context['a93'] = self.dispatchcom2.address
            context['a95'] = intern_utils.no_accent_vietnamese(self.dispatchcom2.director).upper()
            context['a96'] = self.dispatchcom2.position_person_sign
            context['a97'] = self.dispatchcom2.phone_number
            if self.dispatchcom2.fax_number:
                context['a98'] = self.dispatchcom2.fax_number
            context['a99'] = intern_utils.date_time_in_jp(self.dispatchcom2.day_create,self.dispatchcom2.month_create,self.dispatchcom2.year_create)
            context['a100'] = self.developing_employee

            #Phap nhan
            context['a101'] = self.dispatchcom1.name_jp
            context['a102'] = self.dispatchcom1.name_en
            context['a104'] = self.dispatchcom1.name
            context['a105'] = intern_utils.no_accent_vietnamese(self.dispatchcom1.director).upper()
            context['a106'] = self.dispatchcom1.position_director
            # context['a107'] = self.dispatchcom1.address_jp
            context['a108'] = self.dispatchcom1.address_en
            context['a110'] = self.dispatchcom1.phone_number
            if self.dispatchcom1.fax_number:
                context['a111'] = self.dispatchcom1.fax_number

            context['a112'] = self.dispatchcom1.address_en
            context['a113'] = intern_utils.date_time_in_jp(self.dispatchcom1.day_create,self.dispatchcom1.month_create,self.dispatchcom1.year_create)

            counter = 113
            #TTS di cung
            if len(self.interns_pass) >1:
                table_interns = []
                for i, itern in enumerate(self.interns):
                    if i>0:
                        info = {}
                        info['a114'] = intern_utils.no_accent_vietnamese(itern.name).upper()
                        info['a115'] = intern_utils.no_accent_vietnamese(itern.name).upper()
                        info['a116'] = itern.name_in_japan.replace(u'・', ' ')
                        info['a117'] = intern_utils.date_time_in_en(itern.day, itern.month, itern.year)
                        info['a118'] = intern_utils.date_time_in_jp(itern.day, itern.month, itern.year)
                        info['a119'] = intern_utils.date_time_in_en(itern.day, itern.month, itern.year)
                        info['a120'] = intern_utils.date_time_in_vn(itern.day, itern.month, itern.year)
                        info['a121'] = str(intern_utils.get_age_jp(itern.day, itern.month,itern.year))


                        if itern.gender == 'nam':
                            info['a122'] = u'男'
                            info['a123'] = u'MALE'
                        else:
                            info['a122'] = u'女'
                            info['a123'] = u'FEMALE'
                        if itern.marital_status.id is not 2:
                            info['a124'] = u'無'
                        else:
                            info['a124'] = u'有'

                        if itern.identity:
                            info['a125'] = itern.identity
                            info['a127'] = u'%s省公安' % (intern_utils.no_accent_vietnamese(itern.place_cmnd.name))
                        else:
                            info['a15'] = itern.identity_2
                            info['a127'] = u'警察局局長'

                        info['a126'] = intern_utils.date_time_in_jp(itern.day_identity, itern.month_identity,
                                                                    itern.year_identity)

                        if itern.hktt:
                            info['a128'] = intern_utils.no_accent_vietnamese(itern.hktt).upper()
                        info['a129'] = itern.last_time_education
                        info['a130'] = itern.last_school_education_jp
                        info['a131'] = itern.last_school_education
                        info['a132'] = itern.last_time_education

                        info['a133'] = itern.time_employee
                        info['a134'] = itern.job_employee_jp
                        info['a135'] = itern.job_employee_vi

                        if itern.time_employee2 and itern.job_employee2_jp and itern.job_employee2_vi:
                            info['a136'] = itern.time_employee2
                            info['a137'] = itern.job_employee2_jp
                            info['a138'] = itern.job_employee2_vi

                        if itern.time_employee3 and itern.job_employee3_jp and itern.job_employee3_vi:
                            info['a139'] = itern.time_employee3
                            info['a140'] = itern.job_employee3_jp
                            info['a141'] = itern.job_employee3_vi
                        info['a142'] = intern_utils.date_time_in_jp(self.dispatchcom2.day_create,self.dispatchcom2.month_create,self.dispatchcom2.year_create)
                        info['a143'] = itern.time_start_at_pc
                        info['a144'] = "%s (%s)" % (self.dispatchcom2.name, self.job_jp)
                        info['a145'] = "%s (%s)" % (self.dispatchcom2.name_vn, self.job_vi)
                        info['a146'] = itern.total_time_at_pc_jp
                        info['a147'] = itern.total_time_at_pc_vi

                        info['a148'] = intern_utils.no_accent_vietnamese(itern.contact_person).upper()
                        info['a149'] = intern_utils.no_accent_vietnamese(itern.contact_address).upper()
                        info['a150'] = itern.contact_relative.relation_jp
                        info['a151'] = itern.contact_phone
                        #stt
                        info['stt'] = str(i+1)
                        for x in range(1,39):
                            info['s%d'%x] =str(counter+x)
                        counter = counter+38
                        table_interns.append(info)

                context['tbl_intern'] = table_interns

            tpl.render(context)
            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile

    def create_list_of_sent_en(self):
        docs = self.env['intern.document'].search([('name', '=', "list_of_sent")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}
            context['a60'] = self.guild.name_in_en.upper()
            context['a69'] = self.guild.name_of_responsive_romaji
            context['a61'] = self.guild.address_in_jp
            context['a62'] = self.guild.address_in_romaji
            if self.guild.license_number:
                context['a120'] = self.guild.license_number
            if self.guild.fax_number:
                context['a64_65'] = "%s/%s"%(self.guild.phone_number,self.guild.fax_number)
            else:
                context['a64_65'] = self.guild.phone_number

            context['a74'] = self.enterprise_doc.name_jp
            context['a75'] = self.enterprise_doc.name_romaji
            context['a81'] = self.enterprise_doc.name_of_responsive_en
            context['a79'] = self.enterprise_doc.address_romoji
            context['a77'] = self.enterprise_doc.phone_number
            context['a86'] = self.year_expire

            table_interns = []
            for i, intern in enumerate(self.interns_pass):
                info = {}
                info['stt'] = str(i+1)
                info['a3'] = intern_utils.no_accent_vietnamese(intern.name).upper()
                info['a6'] = intern_utils.date_time_in_en(intern.day, intern.month, intern.year)
                if intern.gender == 'nam':
                    info['a13'] = 'MALE'
                else:
                    info['a13'] = 'FEMALE'
                info['a83'] = self.job_en.upper()
                info['a88'] = self.year_departure_doc
                info['a89'] = self.month_departure_doc
                table_interns.append(info)
            context['tbl_intern'] = table_interns
            context['a41'] = intern_utils.date_time_in_en(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)

            context['a91'] = self.position_person_sign
            context['a90'] = intern_utils.no_accent_vietnamese(self.person_sign_proletter)

            context['a102'] = self.dispatchcom1.name_en
            context['a121'] = self.dispatchcom1.license_number
            context['a105'] = intern_utils.no_accent_vietnamese(self.dispatchcom1.director).upper()
            context['a108'] = self.dispatchcom1.address_en

            phone_tax = self.dispatchcom1.phone_number
            if self.dispatchcom1.fax_number and self.dispatchcom1.fax_number != self.dispatchcom1.phone_number:
                phone_tax = phone_tax + "/" + self.dispatchcom1.fax_number
            context['a110_111'] = phone_tax

            tpl.render(context)
            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile

    def create_list_of_sent_jp(self):
        docs = self.env['intern.document'].search([('name', '=', "list_of_sent_jp")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}
            context['a59'] = self.guild.name_in_jp
            context['a60'] = self.guild.name_in_en.upper()
            context['a68'] = self.guild.name_of_responsive_jp
            context['a62'] = self.guild.address_in_romaji
            context['a61'] = self.guild.address_in_jp
            if self.guild.license_number:
                context['a120'] = self.guild.license_number
            if self.guild.fax_number:
                context['a64_65'] = "%s/%s"%(self.guild.phone_number,self.guild.fax_number)
            else:
                context['a64_65'] = self.guild.phone_number

            context['a74'] = self.enterprise_doc.name_jp
            context['a75'] = self.enterprise_doc.name_romaji
            context['a80'] = self.enterprise_doc.name_of_responsive_jp
            context['a76'] = self.enterprise_doc.address_jp
            context['a77'] = self.enterprise_doc.phone_number
            context['a86'] = self.year_expire

            table_interns = []
            for i, intern in enumerate(self.interns_pass):
                info = {}
                info['stt'] = str(i+1)
                info['a3'] = intern_utils.no_accent_vietnamese(intern.name).upper()
                info['a7'] = intern_utils.date_time_in_jp(intern.day,intern.month,intern.year)
                if intern.gender == 'nam':
                    info['a12'] = u'男'
                else:
                    info['a12'] = u'女'
                info['a84'] = self.job_jp
                info['a88'] = self.year_departure_doc
                info['a89'] = self.month_departure_doc
                table_interns.append(info)


            context['tbl_intern'] = table_interns
            context['a40'] = intern_utils.date_time_in_jp(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)

            context['a91_1'] = self.position_person_sign_jp
            context['a90_1'] = intern_utils.no_accent_vietnamese(self.person_sign_proletter)

            context['a102'] = self.dispatchcom1.name_en
            context['a121'] = self.dispatchcom1.license_number
            context['a105'] = intern_utils.no_accent_vietnamese(self.dispatchcom1.director).upper()
            context['a108'] = self.dispatchcom1.address_en

            phone_tax = self.dispatchcom1.phone_number
            if self.dispatchcom1.fax_number and self.dispatchcom1.fax_number != self.dispatchcom1.phone_number:
                phone_tax = phone_tax+"/"+self.dispatchcom1.fax_number
            context['a110_111'] = phone_tax

            tpl.render(context)
            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile

    def create_1_13_1(self):
        doc1_13_1 = self.env['intern.document'].search([('name', '=', "Doc1-13-1")], limit=1)
        if doc1_13_1:
            stream = BytesIO(doc1_13_1[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            tempFile = NamedTemporaryFile(delete=False)
            context = {}
            context['a53'] = self.training_center.name_jp
            context['a57'] = intern_utils.no_accent_vietnamese(self.training_center.responsive_person)
            context['a55'] = intern_utils.date_time_in_jp(self.training_center.day_create,
                                                          self.training_center.month_create,
                                                          self.training_center.year_create)

            context['a56'] = intern_utils.convert_to_vn_phone(self.training_center.phone_number)
            context['a125'] = self.training_center.address_en

            mission = self.training_center.mission
            if '\n' in self.training_center.mission:
                pre = '<w:p><w:r><w:t>'
                post = '</w:t></w:r></w:p>'
                lineBreak = '<w:br/>'
                test = self.training_center.mission.replace('\n',lineBreak)
                mission = pre + test + post
            context['a126'] = mission
            context['a127'] = self.training_center.number_of_employee

            context['a40'] = intern_utils.date_time_in_jp(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)

            tpl.render(context)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile

    def create_1_13_2(self):
        doc1_13_1 = self.env['intern.document'].search([('name', '=', "Doc1-13-2")], limit=1)
        if doc1_13_1:
            stream = BytesIO(doc1_13_1[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            tempFile = NamedTemporaryFile(delete=False)
            context = {}
            context['a102'] = self.dispatchcom1.name_en.upper()
            context['a105'] = intern_utils.no_accent_vietnamese(self.dispatchcom1.director)

            context['a113'] = intern_utils.date_time_in_jp(self.dispatchcom1.day_create,
                                                          self.dispatchcom1.month_create,
                                                          self.dispatchcom1.year_create)

            context['a110_1'] = intern_utils.convert_to_vn_phone(self.dispatchcom1.phone_number)
            context['a112'] = self.dispatchcom1.address_en

            mission = self.dispatchcom1.mission
            if '\n' in mission:
                pre = '<w:p><w:r><w:t>'
                post = '</w:t></w:r></w:p>'
                lineBreak = '<w:br/>'
                test = self.training_center.mission.replace('\n', lineBreak)
                mission = pre + test + post
            context['a128'] = mission
            context['a129'] = self.dispatchcom1.number_of_employee
            context['a130'] = self.dispatchcom1.capital
            context['a131'] = self.dispatchcom1.revenue

            context['a40'] = intern_utils.date_time_in_jp(self.day_create_letter_promotion,
                                                          self.month_create_letter_promotion,
                                                          self.year_create_letter_promotion)

            tpl.render(context)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()
            return tempFile
