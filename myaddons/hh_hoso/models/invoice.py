# -*- coding: utf-8 -*-
from odoo import models, fields, api

from datetime import datetime

from odoo.tools import OrderedSet
import functools
import re
import ast

import logging
_logger = logging.getLogger(__name__)

list_field_report = ['name','create_date','year_expire_char','date_exam_short','room_pttt','status','reason_pause_cancel',
                     'total_pass','date_confirm_form','date_exam','number_man','number_women','source_total','current_status',
                     'interns_clone'
                     ]

remove_fields_searchable = ['day_exam','month_exam','year_exam',
                            'day_supply_form','month_supply_form','year_supply_form','day_check_form','month_check_form',
                            'year_check_form','day_send_form','month_send_form','year_send_form','day_exam','month_exam',
                            'year_exam','day_departure','month_departure','year_departure','day_finish','month_finish','year_finish',
                            'day_cancel_tclt','month_cancel_tclt','year_cancel_tclt','day_cancel_visa_xc','month_cancel_visa_xc',
                            'year_cancel_visa_xc','day_departure2','month_departure2','year_departure2','day_create_letter_promotion',
                            'month_create_letter_promotion','year_create_letter_promotion','day_create_plan_training',
                            'month_create_plan_training','year_create_plan_training','day_start_training','month_start_training',
                            'year_start_training','day_end_training','month_end_training','year_end_training',
                            'day_create_plan_training_report_customer','month_create_plan_training_report_customer',
                            'year_create_plan_training_report_customer','day_pay_finance1','month_pay_finance1','year_pay_finance1',
                            'day_pay_finance2','month_pay_finance2','year_pay_finance2','day_departure_doc','month_departure_doc',
                            'year_departure_doc','day_sign_proletter','month_sign_proletter','year_sign_proletter','interns_clone',
                            'interns_promoted','interns_confirm_exam','interns_escape_exam','interns_pass_new','interns_preparatory',
                            'interns_cancel_pass','interns_departure','write_date','create_uid','write_uid','interns_exam_doc',
                            'interns_pass_doc','order','legal_name','year_expire_char','interns','interns_pass','document']

class InvoiceReport(models.Model):
    _inherit = 'intern.invoice'



    # total_exam_real = fields.Integer('Tổng TTS thi tuyển',store=True,compute='_total_compute')
    #
    # @api.multi
    # @api.depends('interns_clone')
    # def _total_compute(self):
    #     for rec in self:
    #         counter_pass = 0
    #         counter_exam = 0
    #         counter_departure = 0
    #         for intern in self.interns_clone:
    #             if intern.confirm_exam:
    #                 counter_exam+=1
    #             if intern.pass_exam:
    #                 counter_pass+=1
    #             if intern.
    #
    # total_pass_real = fields.Integer('Tổng TTS trúng tuyển')
    # total_departure_real = fields.Integer('Tổng TTS đã xuất cảnh')



    year_expire_char = fields.Char('Thời hạn hợp đồng',store=True,compute='_year_expire')

    @api.multi
    @api.depends('year_expire')
    def _year_expire(self):
        for rec in self:
            rec.year_expire_char = '%d năm'%rec.year_expire



    @api.model
    def fields_get_for_report(self, allfields=None, attributes=None):
        has_access = functools.partial(self.check_access_rights, raise_exception=False)
        readonly = not (has_access('write') or has_access('create'))

        res = {}
        for fname, field in self._fields.iteritems():
            if allfields and fname not in allfields:
                continue
            if field.groups and not self.user_has_groups(field.groups):
                continue
            if fname not in list_field_report:
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

    @api.one
    def confirm_pass(self):
        super(InvoiceReport,self).confirm_pass()
        for intern in self.interns_clone:
            if intern.pass_exam:
                intern.confirm_pass()

    @api.multi
    def write(self, vals):
        tmp = super(InvoiceReport, self).write(vals)
        if tmp:
            for intern in self.interns_clone:
                intern.update_year_expire(self.year_expire)
                intern.update_job_vi(self.job_vi)
                if self.dispatchcom1:
                    intern.update_dispatchcom(self.dispatchcom1.id)
                if self.room_pttt:
                    intern.update_room_pttt(self.room_pttt.id)
                if self.employee_pttt:
                    intern.update_employee_pttt(self.employee_pttt.id)

        return tmp

    @api.model
    def create(self, vals):
        result = super(InvoiceReport, self).create(vals)
        if 'year_expire' in vals:
            for intern in result.interns_clone:
                intern.update_year_expire(vals['year_expire'])
        if 'job_vi' in vals:
            for intern in result.interns_clone:
                intern.update_job_vi(vals['job_vi'])
        if 'dispatchcom1' in vals:
            for intern in result.interns_clone:
                intern.update_dispatchcom(vals['dispatchcom1'])
        if 'room_pttt' in vals:
            for intern in result.interns_clone:
                intern.update_room_pttt(vals['room_pttt'])
        if 'employee_pttt' in vals:
            for intern in result.interns_clone:
                intern.update_employee_pttt(vals['employee_pttt'])
        return result

    def eval_domain(self,domain):
        domains = None
        if domain.startswith('['):
            domains = []
            domain = domain[1:-1]
            tmps = domain.split("),")
            for tmp in tmps:
                domains.append(self.eval_domain(tmp))
        elif domain.startswith('('):
            domains = []
            domain = domain[1:]
            tmps = domain.split(",")
            for tmp in tmps:
                tmp = tmp.strip()
                if tmp.startswith("'"):
                    domains.append(tmp[1:-1])
                elif tmp.startswith('time.strftime'):
                    tmp = tmp[tmp.index('(')+1:tmp.index(')')]
                    tmp = tmp.replace('%Y','%d'%datetime.now().year).replace('%m','%d'%datetime.now().month)
                    domains.append(tmp[1:-1])
                else:
                    domains.append(tmp)

        return domains


    @api.model
    def _read_group_raw(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        self.check_access_rights('read')
        domain_replace = []
        for dm in domain:
            if type(dm) is unicode and dm.startswith("["):
                tmp = self.eval_domain(dm)
                for x in tmp:
                    domain_replace.append(x)
            else:
                domain_replace.append(dm)
        query = self._where_calc(domain_replace)
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
            if f != 'sequence_exam'
            if f != 'sequence_pass'
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
                "array_to_string(ARRAY_AGG(DISTINCT (%s)),' ') AS %s " % (self._inherits_join_calc(self._table, f, query), f))

        for f in bool_fields:
            select_terms.append(
                "COUNT(CASE WHEN %s THEN 1 END) AS %s " % (self._inherits_join_calc(self._table, f, query), f))

        for f in date_fields:
            select_terms.append("ARRAY_AGG(DISTINCT (COALESCE(to_char(%s,'DD-MM-YYYY'),'')) ) AS %s " % (
                self._inherits_join_calc(self._table, f, query), f))



        for f in many2one_fields:
            select_terms.append(u"array_to_string(ARRAY_AGG(DISTINCT (SELECT name from %s WHERE %s.id = %s)),', ') AS %s" % (
                self._fields[f].comodel_name.replace(".", "_"), self._fields[f].comodel_name.replace(".", "_"),
                self._inherits_join_calc(self._table, f, query), f))

        for f in selection_fields:
            if f == 'status':
                select_terms.append(
                    u"array_to_string(ARRAY_AGG(DISTINCT (CASE %s "
                    u"WHEN 4 THEN 'Khởi tạo' "
                    u"WHEN 5 THEN 'Tiến cử' "
                    u"WHEN 1 THEN 'Thi tuyển' "
                    u"WHEN 2 THEN 'Chốt trúng tuyển' "
                    u"WHEN 3 THEN 'Hoàn thành' "
                    u"WHEN 6 THEN 'Tạm dừng' "
                    u"WHEN 7 THEN 'Huỷ bỏ' "
                    u"END)),', ') AS %s " % (
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



    total_pass = fields.Integer('Số lượng trúng tuyển',store=True,compute='_compute_total_pass')

    current_status = fields.Char('Tình trạng mới nhất về đơn hàng',store=True,compute='_compute_current_status')

    @api.one
    @api.depends('interns_clone')
    def _compute_total_pass(self):
        temp_total_pass = 0
        for intern in self.interns_clone:
            if intern.pass_exam and not intern.cancel_pass:
                temp_total_pass+=1
        self.total_pass = temp_total_pass

    @api.one
    @api.depends('interns_clone','status')
    def _compute_current_status(self):
        if self.status == 4:
            temp_total = 0
            if self.interns_clone:
                temp_total = len(self.interns_clone)
            self.current_status = u'Có %d form trong danh sách dự kiến tiến cử'%temp_total
        elif self.status == 5:
            temp_total = 0
            for intern in self.interns_clone:
                if intern.promoted:
                    temp_total +=1
            self.current_status = u'Có %d form được tiến cử' % temp_total
        elif self.status == 1:
            temp_total = 0
            temp_total_cancel_exam = 0
            for intern in self.interns_clone:
                if intern.confirm_exam:
                    temp_total += 1
                if intern.escape_exam:
                    temp_total_cancel_exam +=1
            self.current_status = u'Có %d form chốt thi tuyển' % temp_total
            if temp_total_cancel_exam>0:
                self.current_status = self.current_status + u". Có %d tts rút bỏ chốt thi"%temp_total_cancel_exam
        # elif self.status == '2':
        else:
            temp_total_pass = 0
            temp_total_preparatory = 0
            temp_total_cancel_pass = 0
            for intern in self.interns_clone:
                if intern.pass_exam:
                    temp_total_pass +=1
                if intern.preparatory_exam:
                    temp_total_preparatory +=1
                if intern.cancel_pass:
                    temp_total_cancel_pass +=1
            self.current_status = u'Có %d tts trúng tuyển' % temp_total_pass
            if temp_total_preparatory>0:
                self.current_status += u', %d tts dự bị'%temp_total_preparatory
            if temp_total_cancel_pass>0:
                self.current_status += u', %d tts huỷ trúng tuyển'%temp_total_cancel_pass