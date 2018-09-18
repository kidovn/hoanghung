# -*- coding: utf-8 -*-
from odoo import models, fields, api

from datetime import datetime
import functools
from odoo.tools import OrderedSet

import logging
_logger = logging.getLogger(__name__)

fields_report_intern = ['name','custom_id','gender','enter_source','identity','identity_2','cmnd_or_tcc','date_identity_short','place_cmnd',
                     'date_of_birth_short','name_in_japan','address','province','avatar','marital_status','height',
                     'weight','vision_left','vision_right','blood_group','note_health','check_kureperin','certification',
                     'phone_number','phone_number_relative','relative_note','date_sent_doc_short','logic_percentage','add_percentage',
                     'calculation_percentage','notice_percentage','iq_percentage','average','room_recruitment','recruitment_employee',
                     'recruitment_r_employee','date_pass_short','date_join_school_short','date_leave_short','date_liquidation_short',
                     'blindness','smoking','preferred_hand','surgery','surgery_content','drink_alcohol','specialized','favourite',
                     'strong','weak','teammate','cooking','diseases','family_income','motivation','income_after_three_year',
                     'job_after_return','prefer_object','memory','valuable','education_status','education_content','family_member_in_jp',
                     'family_accept','educations','employments','family_members','have_form','have_health','have_deposit',
                     'discipline','deportation','exp_sew','exp_mechanical','exp_building','exp_note',
                     'hktt','contact_person','contact_relative','contact_phone','contact_address','last_time_education',

                     ]
fields_report_intern_clone = ['pass_exam','cancel_pass','preparatory_exam',
                           'issues_before','issues_after','admission_late','visa_failure','departure']

fields_report_invoice = ['invoices_promoted','invoices_exam','invoices_pass']

fields_date_intern = ['create_date']
fields_date_internclone = ['date_pass']


remove_fields_searchable = ['add_correct','add_done','calculation_correct','calculation_done','logic_correct','logic_done',
                            'notice_correct','notice_done','total_question','user_access','intern_status',
                            'education_status','education_content','family_member_in_jp','family_accept','educations',
                            'employments','family_members','employments_vi','interndn_id','internks_id','internhs_id',
                            'contact_person','contact_relative','contact_phone','contact_address','last_education_from_month',
                            'last_education_from_year','last_education_to_month','last_education_to_year','last_education_from_month2',
                            'last_education_from_year2','last_education_to_month2','last_education_to_year2','last_school_education',
                            'last_school_education_jp','last_school_education2','last_school_education_jp2','time_employee_from_month',
                            'time_employee_from_year','time_employee_to_month','time_employee_to_year','time_employee2_from_month',
                            'time_employee2_from_year','time_employee2_from_year','time_employee2_to_month','time_employee2_to_year',
                            'job_employee2_jp','job_employee2_vi','time_employee3','job_employee3_jp','job_employee3_vi',
                            'job_employee_jp','job_employee_vi','time_employee3_from_month','time_employee3_from_year',
                            'time_employee3_to_month','time_employee3_to_year','time_employee4','job_employee4_jp','job_employee4_vi',
                            'time_employee4_from_month','time_employee4_from_year','time_employee4_to_month','time_employee4_to_year',
                            'time_employee5','job_employee5_jp','job_employee5_vi','time_employee5_from_month','time_employee5_from_year',
                            'time_employee5_to_month','time_employee5_to_year','time_start_at_pc','time_start_at_pc_from_month',
                            'time_start_at_pc_from_year','day_sent_doc','month_sent_doc','year_sent_doc','day_identity','month_identity',
                            'year_identity','place_cmnd','enter_source_tmp','sequence_exam','sequence_pass','valuable','memory','prefer_object',
                            'job_after_return','income_after_three_year','motivation','family_income','day','month','year'
                            ]


class InternReport(models.Model):
    _inherit = 'intern.intern'


    date_identity_short = fields.Date("Ngày cấp cmnd", store=False, compute='_date_of_identity_short')

    @api.multi
    @api.depends('day_identity', 'month_identity', 'year_identity')
    def _date_of_identity_short(self):
        for rec in self:
            if rec.day_identity and rec.month_identity and rec.year_identity:
                try:
                    rec.date_identity_short = datetime.strptime('%s-%s-%s' % (rec.year_identity, rec.month_identity, rec.day_identity), '%Y-%m-%d')
                except:
                    return None
            else:
                rec.date_identity_short = None

    date_sent_doc_short = fields.Date("Ngày gửi hồ sơ", store=True, compute='_date_send_doc_short')

    @api.multi
    @api.depends('day_sent_doc', 'month_sent_doc', 'year_sent_doc')
    def _date_send_doc_short(self):
        for rec in self:
            try:
                if rec.day_sent_doc and rec.month_sent_doc and rec.year_sent_doc:
                    rec.date_sent_doc_short = datetime.strptime('%s-%s-%s' % (rec.year_sent_doc, rec.month_sent_doc, rec.day_sent_doc), '%Y-%m-%d')
                else:
                    rec.date_sent_doc_short = None
            except:
                rec.date_sent_doc_short = None



    def fields_get_for_report(self, allfields=None, attributes=None):
        """ fields_get([fields][, attributes])

        Return the definition of each field.

        The returned value is a dictionary (indiced by field name) of
        dictionaries. The _inherits'd fields are included. The string, help,
        and selection (if present) attributes are translated.

        :param allfields: list of fields to document, all if empty or not provided
        :param attributes: list of description attributes to return for each field, all if empty or not provided
        """
        has_access = functools.partial(self.check_access_rights, raise_exception=False)
        readonly = not (has_access('write') or has_access('create'))

        res = {}
        for fname, field in self._fields.iteritems():
            if allfields and fname not in allfields:
                continue
            if field.groups and not self.user_has_groups(field.groups):
                continue
            if fname not in fields_report_intern:
                continue

            description = field.get_description(self.env)
            if readonly:
                description['readonly'] = True
                description['states'] = {}
            if attributes:
                description = {key: val
                               for key, val in description.iteritems()
                               if key in attributes}
            res[fname] = description

        return res

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        has_access = functools.partial(self.check_access_rights, raise_exception=False)
        readonly = not (has_access('write') or has_access('create'))

        res = {}
        for fname, field in self._fields.iteritems():
            if allfields and fname not in allfields:
                continue
            if field.groups and not self.user_has_groups(field.groups):
                continue

            description = field.get_description(self.env)
            if readonly:
                description['readonly'] = True
                description['states'] = {}
            if attributes:
                description = {key: val
                               for key, val in description.iteritems()
                               if key in attributes}
            if fname in remove_fields_searchable:
                description['searchable'] = False
            res[fname] = description

        return res





class InternCloneReport(models.Model):
    _inherit = 'intern.internclone'

    # date_promoted = fields.Datetime(string='Ngày tiến cử')
    # user_promoted = fields.Many2one('res.users', string='Người tiến cử')
    # date_confirm_exam = fields.Datetime(string='Ngày chốt thi tuyển')
    # user_confirm_exam = fields.Many2one('res.users', string='Người chốt thi tuyển')


    year_expire = fields.Char("Thời hạn hợp đồng")
    def update_year_expire(self, years):
        self.write({
            'year_expire': "%d năm"%years,
        })

    job_vi = fields.Char("Ngành nghề")
    def update_job_vi(self, job):
        self.write({
            'job_vi': job,
        })

    dispatchcom = fields.Many2one('dispatchcom1', string='Pháp nhân')

    def update_dispatchcom(self, dispatchcom):
        self.write({
            'dispatchcom': dispatchcom,
        })

    room_pttt = fields.Many2one('department',string='Phòng PTTT')
    def update_room_pttt(self, room_pttt):
        self.write({
            'room_pttt': room_pttt,
        })

    employee_pttt = fields.Many2one('hh.employee',string='Cán bộ PTTT')

    def update_employee_pttt(self, employee_pttt):
        self.write({
            'employee_pttt': employee_pttt,
        })

    @api.model
    def _read_group_raw(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        self.check_access_rights('read')
        query = self._where_calc(domain)
        fields = fields or [f.name for f in self._fields.itervalues() if f.store]

        groupby = [groupby] if isinstance(groupby, basestring) else list(OrderedSet(groupby))
        groupby_list = groupby[:1] if lazy else groupby
        annotated_groupbys = [self._read_group_process_groupby(gb, query) for gb in groupby_list]
        groupby_fields = [g['field'] for g in annotated_groupbys]
        order = orderby or ','.join([g for g in groupby_list])
        groupby_dict = {gb['groupby']: gb for gb in annotated_groupbys}

        self._apply_ir_rules(query, 'read')
        for gb in groupby_fields:
            assert gb in fields, "Fields in 'groupby' must appear in the list of fields to read (perhaps it's missing in the list view?)"
            assert gb in self._fields, "Unknown field %r in 'groupby'" % gb
            gb_field = self._fields[gb].base_field
            assert gb_field.store and gb_field.column_type, "Fields in 'groupby' must be regular database-persisted fields (no function or related fields), or function fields with store=True"

        aggregated_fields = [
            f for f in fields
            if f != 'sequence'
            if f !='sequence_exam'
            if f !='sequence_pass'
            if f not in groupby_fields
            for field in [self._fields.get(f)]
            if field
            if field.group_operator
            if field.base_field.store and field.base_field.column_type
        ]

        char_fields = [
            f for f in fields
            if f != 'sequence'
            if f not in groupby_fields
            for field in [self._fields.get(f)]
            if field
            if field.type == 'char'
            if field.base_field.store and field.base_field.column_type
        ]

        text_fields = [
            f for f in fields
            if f != 'sequence'
            if f not in groupby_fields
            for field in [self._fields.get(f)]
            if field
            if field.type == 'text'
            if field.base_field.store and field.base_field.column_type
        ]

        bool_fields = [
            f for f in fields
            if f != 'sequence'
            if f not in groupby_fields
            for field in [self._fields.get(f)]
            if field
            if field.type == 'boolean'
            if field.base_field.store and field.base_field.column_type
        ]

        date_fields = [
            f for f in fields
            if f != 'sequence'
            if f not in groupby_fields
            for field in [self._fields.get(f)]
            if field
            if field.type == 'datetime' or field.type == 'date'
            if field.base_field.store and field.base_field.column_type
        ]

        many2one_fields = [
            f for f in fields
            if f != 'sequence'
            if f not in groupby_fields
            for field in [self._fields.get(f)]
            if field
            if field.type == 'many2one'
            if field.base_field.store and field.base_field.column_type
        ]

        selection_fields = [
            f for f in fields
            if f != 'sequence'
            if f not in groupby_fields
            for field in [self._fields.get(f)]
            if field
            if field.type == 'selection'
            if field.base_field.store and field.base_field.column_type
        ]

        field_formatter = lambda f: (
            self._fields[f].group_operator,
            self._inherits_join_calc(self._table, f, query),
            f,
        )
        select_terms = ['%s(%s) AS "%s" ' % field_formatter(f) for f in aggregated_fields]

        for f in char_fields:
            select_terms.append(
                "array_to_string(ARRAY_AGG(DISTINCT (%s)),',') AS %s " % (self._inherits_join_calc(self._table, f, query), f))

        for f in text_fields:
            select_terms.append(
                "array_to_string(ARRAY_AGG(DISTINCT (%s)),',') AS %s " % (self._inherits_join_calc(self._table, f, query), f))

        for f in bool_fields:
            select_terms.append(
                "COUNT(CASE WHEN %s THEN 1 END) AS %s " % (self._inherits_join_calc(self._table, f, query), f))

        for f in date_fields:
            select_terms.append("ARRAY_AGG(DISTINCT (COALESCE(to_char(%s,'DD-MM-YYYY'),'')) )  AS %s " % (
            self._inherits_join_calc(self._table, f, query), f))

        for f in selection_fields:
            if f == 'gender':
                select_terms.append(
                    u"array_to_string(ARRAY_AGG(DISTINCT (CASE %s WHEN 'nam' THEN 'Nam' WHEN 'nu' THEN 'Nữ' END)),', ') AS %s " % (
                    self._inherits_join_calc(self._table, f, query), f))
            elif f == 'enter_source':
                select_terms.append(
                    u"array_to_string(ARRAY_AGG(DISTINCT (CASE %s WHEN '1' THEN 'Ngắn hạn' WHEN '2' THEN 'Dài hạn' WHEN '3' THEN 'Ban chỉ đạo' ELSE '' END)),', ') AS %s " % (
                        self._inherits_join_calc(self._table, f, query), f))
        #
        # for f in many2one_fields:
        #     _logger.info("AAA %s"%self._fields[f].comodel_name)

        for f in many2one_fields:
            if f == 'dispatchcom':
                select_terms.append(u"array_to_string(ARRAY_AGG(DISTINCT (SELECT name_short from %s WHERE %s.id = %s)),', ') AS %s" % (
                self._fields[f].comodel_name.replace(".", "_"), self._fields[f].comodel_name.replace(".", "_"),
                self._inherits_join_calc(self._table, f, query), f))
            elif f== 'recruitment_employee':
                select_terms.append(u"array_to_string(ARRAY_AGG(DISTINCT (SELECT name_related from %s WHERE %s.id = %s)),', ') AS %s" % (
                    self._fields[f].comodel_name.replace(".", "_"), self._fields[f].comodel_name.replace(".", "_"),
                    self._inherits_join_calc(self._table, f, query), f))
            else:
                select_terms.append(u"array_to_string(ARRAY_AGG(DISTINCT (SELECT name from %s WHERE %s.id = %s)),', ') AS %s" % (
                    self._fields[f].comodel_name.replace(".", "_"), self._fields[f].comodel_name.replace(".", "_"),
                    self._inherits_join_calc(self._table, f, query), f))

        for gb in annotated_groupbys:
            select_terms.append('%s as "%s" ' % (gb['qualified_field'], gb['groupby']))

        groupby_terms, orderby_terms = self._read_group_prepare(order, aggregated_fields, annotated_groupbys, query)
        from_clause, where_clause, where_clause_params = query.get_sql()
        if lazy and (len(groupby_fields) >= 2 or not self._context.get('group_by_no_leaf')):
            count_field = groupby_fields[0] if len(groupby_fields) >= 1 else '_'
        else:
            count_field = '_'
        count_field += '_count'

        prefix_terms = lambda prefix, terms: (prefix + " " + ",".join(terms)) if terms else ''
        prefix_term = lambda prefix, term: ('%s %s' % (prefix, term)) if term else ''

        query = """
                    SELECT min("%(table)s".id) AS id, count("%(table)s".id) AS "%(count_field)s" %(extra_fields)s
                    FROM %(from)s
                    %(where)s
                    %(groupby)s
                    %(orderby)s
                    %(limit)s
                    %(offset)s
                """ % {
            'table': self._table,
            'count_field': count_field,
            'extra_fields': prefix_terms(',', select_terms),
            'from': from_clause,
            'where': prefix_term('WHERE', where_clause),
            'groupby': prefix_terms('GROUP BY', groupby_terms),
            'orderby': prefix_terms('ORDER BY', orderby_terms),
            'limit': prefix_term('LIMIT', int(limit) if limit else None),
            'offset': prefix_term('OFFSET', int(offset) if limit else None),
        }
        self._cr.execute(query, where_clause_params)
        fetched_data = self._cr.dictfetchall()

        if not groupby_fields:
            return fetched_data

        many2onefields = [gb['field'] for gb in annotated_groupbys if gb['type'] == 'many2one']
        if many2onefields:
            data_ids = [r['id'] for r in fetched_data]
            many2onefields = list(set(many2onefields))
            data_dict = {d['id']: d for d in self.browse(data_ids).read(many2onefields)}
            for d in fetched_data:
                d.update(data_dict[d['id']])

        data = map(lambda r: {k: self._read_group_prepare_data(k, v, groupby_dict) for k, v in r.iteritems()},
                   fetched_data)
        result = [self._read_group_format_result(d, annotated_groupbys, groupby, domain) for d in data]
        if lazy:
            # Right now, read_group only fill results in lazy mode (by default).
            # If you need to have the empty groups in 'eager' mode, then the
            # method _read_group_fill_results need to be completely reimplemented
            # in a sane way
            result = self._read_group_fill_results(
                domain, groupby_fields[0], groupby[len(annotated_groupbys):],
                aggregated_fields, count_field, result, read_group_order=order,
            )
        return result

    @api.model
    def fields_get_for_report(self, allfields=None, attributes=None):
        return self.fields_get(allfields,attributes)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        has_access = functools.partial(self.check_access_rights, raise_exception=False)
        readonly = not (has_access('write') or has_access('create'))

        res = {}
        for fname, field in self._fields.iteritems():
            if allfields and fname not in allfields:
                continue
            if field.groups and not self.user_has_groups(field.groups):
                continue

            description = field.get_description(self.env)
            if readonly:
                description['readonly'] = True
                description['states'] = {}
            if attributes:
                description = {key: val
                               for key, val in description.iteritems()
                               if key in attributes}
            if fname in remove_fields_searchable:
                description['searchable'] = False
            res[fname] = description

        return res


