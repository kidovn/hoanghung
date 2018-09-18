# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.hh_intern.models import intern_utils
from tempfile import TemporaryFile, NamedTemporaryFile
from io import BytesIO
from cStringIO import StringIO
from docxtpl import DocxTemplate, InlineImage, CheckedBox, CheckBox, RichText, Tick
from docx.shared import Mm, Inches
from docx import Document

class Member(models.Model):
    _name = 'family.member'

    info = fields.Many2one("intern.hokhau", required=True, ondelete='cascade')

    name = fields.Char("Họ và tên", required=True)

    name_jp = fields.Char('Họ và tên Tiếng Nhật')

    @api.onchange('name')  # if these fields are changed, call method
    def name_change(self):
        if self.name:
            self.name_without_signal = intern_utils.no_accent_vietnamese(self.name)
            tmp = self.convertToJP(intern_utils.fix_accent_2(intern_utils.no_accent_vietnamese2(self.name)))
            if tmp is not None:
                self.name_jp = tmp

    name_other = fields.Char('Họ và tên gọi khác')
    name_other_jp = fields.Char('Họ và tên gọi khác Tiếng Nhật')

    @api.onchange('name_other')  # if these fields are changed, call method
    def name_change(self):
        if self.name:
            self.name_without_signal = intern_utils.no_accent_vietnamese(self.name_other)
            tmp = self.convertToJP(intern_utils.fix_accent_2(intern_utils.no_accent_vietnamese2(self.name_other)))
            if tmp is not None:
                self.name_other_jp = tmp

    def convertToJP(self,name):
        words = name.split()
        final = ""
        for i,word in enumerate(words):
            jps = self.env['intern.translator'].search([('vi_word','=',word.upper())],limit=1)
            if jps:
                if i > 0:
                    final = final+u"・"
                final = final+jps[0].jp_word
            else:
                return ""
        return final

    day = fields.Char("Ngày sinh", size=2)
    month = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                              ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                              ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng sinh")

    year = fields.Char("Năm sinh", size=4)

    relation = fields.Many2one('relation', string='Quan hệ với chủ hộ')

    gender = fields.Selection([('nam', 'Nam'), ('nu', 'Nữ')], string='Giới tính')

    address = fields.Char('Quê quán')
    address_jp = fields.Char('Quê quán (Tiếng Nhật)')
    folk = fields.Char('Dân tộc',default=u'キン')
    nation = fields.Char('Quốc tịch',default=u'ベトナム')

    identity = fields.Char('Số CMND')

    # day_identity = fields.Char("Ngày", size=2)
    # month_identity = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
    #                                    ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
    #                                    ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng")
    #
    # year_identity = fields.Char("Năm", size=4)
    #
    # date_identity = fields.Char("Ngày cấp", store=False, compute='_date_of_identity')
    #
    # @api.one
    # @api.depends('day_identity', 'month_identity', 'year_identity')
    # def _date_of_identity(self):
    #     if self.day_identity and self.month_identity and self.year_identity:
    #         self.date_identity = u"%s Tháng %s Năm %s" % (self.day_identity, self.month_identity, self.year_identity)
    #     else:
    #         self.date_identity = ""


    passport_number = fields.Char('Số hộ chiếu')

    job_place = fields.Char('Nghề nghiệp, nơi làm việc')

    day_arrive = fields.Char("Ngày chuyển đến", size=2)
    month_arrive = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                              ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                              ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng chuyển đến")

    year_arrive = fields.Char("Năm chuyển đến", size=4)

    address_before_arrive = fields.Char('Địa chỉ trước khi chuyển đến')
    address_before_arrive_jp = fields.Char('Địa chỉ trước khi chuyển đến TN')

    day_sign = fields.Char("Ngày ký", size=2)
    month_sign = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                     ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                     ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng ký")

    year_sign = fields.Char("Năm ký", size=4)

    official = fields.Char('Cán bộ đăng ký')
    official_jp = fields.Char('Cán bộ đăng ký TN')
    truong_ca = fields.Char('Trưởng CA')
    truong_ca_jp = fields.Char('Trưởng CA TN')


    reason_remove_dktt = fields.Char('Lý do xoá ĐK thường trú')

    official_remove = fields.Char('Cán bộ đăng ký')
    official_remove_jp = fields.Char('Cán bộ đăng ký TN')
    truong_ca_remove = fields.Char('Trưởng CA')
    truong_ca_remove_jp = fields.Char('Trưởng CA TN')

    day_sign_remove = fields.Char("Ngày ký", size=2)
    month_sign_remove = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                     ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                     ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng ký")

    year_sign_remove = fields.Char("Năm ký", size=4)


class Family(models.Model):
    # _name = 'intern.intern'

    _inherit = 'intern.intern'

    shk_no = fields.Char('Số HK')
    address_village = fields.Char('Xã, phường')
    address_village_jp = fields.Char('Xã, phường (Tiếng Nhật)')
    address_district = fields.Char('Huyện')
    address_district_jp = fields.Char('Huyện (Tiếng Nhật)')
    address_province = fields.Char('Tỉnh')
    # address_province_jp = fields.Char('Tỉnh (Tiếng Nhật)')

    day_sign = fields.Char("Ngày ký", size=2)
    month_sign = fields.Selection([('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                   ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                   ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), ], "Tháng ký")

    year_sign = fields.Char("Năm ký", size=4)

    truong_ca = fields.Char('Trưởng CA')
    # truong_ca_jp = fields.Char('Trưởng CA')

    document_no = fields.Char('Hồ sơ hộ khẩu số')

    book_dktt_no = fields.Char('Sổ ĐK thường trú số')

    page_no = fields.Char('Tờ số')


    members = fields.One2many('family.member',"info", string='Thành viên')

    def download_shk(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_shk?id=%s&filename=%s.zip' % (
                str(self.id), 'test'),
            'target': 'self', }

    def date_time_in_en(self,day, month, year):
        if not day:
            day = '  '
        if not month:
            month = '  '
        if not year:
            year = '  '
        return u'%s/%s/%s' % (year, month,day )

    def date_time_in_jp_missing(self, day, month, year):
        if not day:
            day = '  '
        if not month:
            month = '  '
        if not year:
            year = '  '
        return u'%s年%s月%s日' % (year, month, day)

    def generate_shk(self):
        docs = self.env['intern.document'].search([('name', '=', "SHK_1")], limit=1)
        if docs:
            stream = BytesIO(docs[0].attachment.decode("base64"))
            tpl = DocxTemplate(stream)
            context = {}
            context['tinh'] = u'%s'%self.address_province
            context['no_shk'] = self.shk_no
            master = None
            for member in self.members:
                if member.relation is None:
                    master = member
                    break
            if master is not None:
                context['ch'] = master.name
            context['huyen'] = u'%s'%self.address_district
            context['xa'] = u'%s'%self.address_village
            context['date_sign'] = self.date_time_in_jp_missing(self.day_sign,self.month_sign,self.year_sign)
            context['ca'] = self.truong_ca
            context['doc_no'] = self.document_no
            context['book_no'] = self.book_dktt_no
            context['page'] = self.page_no

            table_content = []
            # table_cols = {}
            # table_cols['cols'] = ['XXXX']
            # table_content.append(table_cols)
            for i in range(0,int((len(self.members)+1)/2)):
                table_cols = {}
                cols = []
                colm1 = {}
                if not self.members[i*2].relation:
                    colm1['relation'] = u'世帯主'
                else:
                    colm1['relation'] = u'世帯主との続柄：%s'%self.members[i*2].relation.relation_jp
                colm1['name'] = u'%s'%self.members[i*2].name
                if self.members[i*2].name_other:
                    colm1['other_name'] = u'%s' % self.members[i * 2].name_other
                colm1['birthday'] = self.date_time_in_en(self.members[i * 2].day,self.members[i * 2].month,self.members[i * 2].year)
                colm1['address'] = self.members[i * 2].address
                colm1['folk'] = self.members[i * 2].folk
                colm1['nation'] = self.members[i * 2].nation
                if self.members[i * 2].identity:
                    colm1['cmnd'] = self.members[i * 2].identity
                if self.members[i * 2].passport_number:
                    colm1['pp'] = self.members[i * 2].passport_number
                if self.members[i * 2].job_place:
                    colm1['job'] = self.members[i * 2].job_place
                colm1['date_arrive'] = self.date_time_in_en(self.members[i * 2].day_arrive,self.members[i * 2].month_arrive,self.members[i * 2].year_arrive)
                if self.members[i * 2].address_before_arrive:
                    colm1['add_before_arrive'] = self.members[i * 2].address_before_arrive
                if self.members[i * 2].official:
                    colm1['officer'] = self.members[i * 2].official
                if self.members[i * 2].truong_ca:
                    colm1['ca'] = self.members[i * 2].truong_ca
                colm1['date_sign'] = self.date_time_in_jp_missing(self.members[i * 2].day_sign,self.members[i * 2].month_sign,self.members[i * 2].year_sign)
                if self.members[i * 2].reason_remove_dktt:
                    colm1['reason_remove'] = self.members[i * 2].reason_remove_dktt
                if self.members[i * 2].official_remove:
                    colm1['officer_remove'] = self.members[i * 2].official_remove
                colm1['date_sign_remove'] = self.date_time_in_jp_missing(self.members[i * 2].day_sign_remove,self.members[i * 2].month_sign_remove,self.members[i * 2].year_sign_remove)
                if self.members[i * 2].truong_ca_remove:
                    colm1['ca_remove'] = self.members[i * 2].truong_ca_remove
                cols.append(colm1)
                if i*2+1<len(self.members):
                    colm2 = {}
                    if not self.members[i * 2+1].relation:
                        colm2['relation'] = u'世帯主'
                    else:
                        colm2['relation'] = u'世帯主との続柄：%s' % self.members[i * 2+1].relation.relation_jp
                    colm2['name'] = u'%s' % self.members[i * 2 +1].name
                    if self.members[i * 2+1].name_other:
                        colm2['other_name'] = u'%s' % self.members[i * 2+1].name_other
                    colm2['birthday'] = self.date_time_in_en(self.members[i * 2+1].day, self.members[i * 2+1].month,
                                                             self.members[i * 2+1].year)
                    colm2['address'] = self.members[i * 2+1].address
                    colm2['folk'] = self.members[i * 2+1].folk
                    colm2['nation'] = self.members[i * 2+1].nation
                    if self.members[i * 2+1].identity:
                        colm2['cmnd'] = self.members[i * 2+1].identity
                    if self.members[i * 2+1].passport_number:
                        colm2['pp'] = self.members[i * 2+1].passport_number
                    if self.members[i * 2+1].job_place:
                        colm2['job'] = self.members[i * 2+1].job_place
                    colm2['date_arrive'] = self.date_time_in_en(self.members[i * 2+1].day_arrive,
                                                                self.members[i * 2+1].month_arrive,
                                                                self.members[i * 2+1].year_arrive)
                    if self.members[i * 2+1].address_before_arrive:
                        colm2['add_before_arrive'] = self.members[i * 2+1].address_before_arrive
                    if self.members[i * 2+1].official:
                        colm2['officer'] = self.members[i * 2+1].official
                    if self.members[i * 2+1].truong_ca:
                        colm2['ca'] = self.members[i * 2+1].truong_ca
                    colm2['date_sign'] = self.date_time_in_jp_missing(self.members[i * 2+1].day_sign,
                                                                              self.members[i * 2+1].month_sign,
                                                                              self.members[i * 2+1].year_sign)
                    if self.members[i * 2+1].reason_remove_dktt:
                        colm2['reason_remove'] = self.members[i * 2+1].reason_remove_dktt
                    if self.members[i * 2+1].official_remove:
                        colm2['officer_remove'] = self.members[i * 2+1].official_remove
                    colm2['date_sign_remove'] = self.date_time_in_jp_missing(
                        self.members[i * 2+1].day_sign_remove, self.members[i * 2+1].month_sign_remove,
                        self.members[i * 2+1].year_sign_remove)
                    if self.members[i * 2+1].truong_ca_remove:
                        colm2['ca_remove'] = self.members[i * 2+1].truong_ca_remove
                    cols.append(colm2)
                table_cols['cols'] = cols
                table_content.append(table_cols)

            context['tbl_contents'] = table_content

            tpl.render(context)
            tempFile = NamedTemporaryFile(delete=False)
            tpl.save(tempFile)
            tempFile.flush()
            tempFile.close()

            fp = StringIO()
            tpl.save(fp)
            fp.seek(0)
            data = fp.read()
            fp.close()
            return data


class Invoice(models.Model):
    _inherit = 'intern.invoice'

    def translate_shk(self):
        view_id = self.env.ref('hh_sohokhau.view_manage_invoice_sohokhau').id
        context = self._context.copy()
        return {
            'name': 'form_name',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'intern.invoice',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': context,
        }