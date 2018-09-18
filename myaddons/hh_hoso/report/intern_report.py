# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models
from datetime import datetime

from odoo.tools import frozendict, lazy_classproperty, lazy_property, ormcache, \
                   Collector, LastOrderedSet, OrderedSet

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

import pytz
import logging
_logger = logging.getLogger(__name__)

class InternReport(models.Model):
    _name = "intern.report"
    _auto = False

    intern_id = fields.Many2one('intern.intern', 'TTS', readonly=True)

    custom_id = fields.Char("Mã số", readonly=True)

    date_of_birth_short = fields.Date("Ngày sinh")

    gender = fields.Selection([('nam', 'Nam'), ('nu', 'Nữ')], string='Giới tính', readonly=True)

    cmnd = fields.Char("CMND/Thẻ căn cước", readonly=True)

    province = fields.Many2one('province','Quê quán')


    recruitment_employee = fields.Many2one('hh.employee', 'Cán bộ tuyển dụng', readonly=True)

    room_recruitment = fields.Many2one('department', 'Phòng tuyển dụng', readonly=True)

    enter_source_short = fields.Boolean('Nguồn ngắn hạn', readonly=True)
    enter_source_long = fields.Boolean('Nguồn Dài hạn', readonly=True)
    enter_source_bcd = fields.Boolean('Nguồn Ban chỉ đạo', readonly=True)

    escape_source = fields.Boolean('Rút bỏ nguồn', readonly=True)

    date_enter_source = fields.Date('Ngày vào nguồn', readonly=True)

    date_escape_source = fields.Date('Ngày rút bỏ nguồn', readonly=True)

    date_create_info = fields.Datetime('Ngày tạo thông tin', readonly=True)

    # escape_exam = fields.Integer('Rút bỏ ĐH', readonly=True)



    def _select(self):
        select_str = """
            SELECT intern.id as id,
                intern.id as intern_id,
                (CASE WHEN internks.day<>'' AND internks.month<>'' AND internks.year <>''
                    THEN to_date(CONCAT(internks.day,' ',internks.month,' ',internks.year),'DD MM YYYY') 
                ELSE NULL 
                END ) as date_of_birth_short,
                intern.create_date as date_create_info,
                (CASE WHEN internks.identity is not NULL then internks.identity ELSE internks.identity_2 END) as cmnd,
                intern.custom_id as custom_id,
                internks.province as province,
                internks.room_recruitment as room_recruitment,
                internks.recruitment_employee as recruitment_employee, 
                internks.gender AS gender,
                (CASE WHEN internks.enter_source_tmp = '1' THEN TRUE ELSE FALSE END) AS enter_source_short,
                (CASE WHEN internks.enter_source_tmp = '2' THEN TRUE ELSE FALSE END) AS enter_source_long,
                (CASE WHEN internks.enter_source_tmp = '3' THEN TRUE ELSE FALSE END) AS enter_source_bcd,
                (CASE WHEN internks.enter_source = '4' THEN TRUE ELSE FALSE END) AS escape_source,
                internks.date_enter_source AS date_enter_source,
                internks.date_escape_source AS date_escape_source
            """

        # ,
        # (SELECT COUNT( *)
        # FROM?
        # intern_internclone
        # WHERE
        # intern_internclone.intern_id = intern.id
        # AND
        # intern_internclone.issues_raise = TRUE) AS
        # escape_exam
        return select_str

    def _from(self):
        from_str = """
            intern_intern intern
            LEFT JOIN intern_internks internks ON intern.internks_id = internks.id
              
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY intern.id,
            intern.create_date,
            internks.day,
            internks.month,
            internks.year,
            internks.identity,
            internks.identity_2,
            intern.custom_id,
            internks.room_recruitment,
            internks.recruitment_employee,
            internks.gender,
            internks.province,
            internks.enter_source,
            internks.enter_source_tmp,
            internks.date_enter_source,
            internks.date_escape_source
            """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                %s
                FROM ( %s )
                %s
                )""" % (self._table, self._select(), self._from(), self._group_by()))


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
            select_terms.append("array_to_string(ARRAY_AGG(DISTINCT (%s)),', ') AS %s " %(self._inherits_join_calc(self._table, f, query),f))

        for f in bool_fields:
            select_terms.append("COUNT(CASE WHEN %s THEN 1 END) AS %s " %(self._inherits_join_calc(self._table, f, query),f))

        for f in date_fields:
            select_terms.append("ARRAY_AGG(DISTINCT (COALESCE(to_char(%s,'DD-MM-YYYY'),'')) ) AS %s " %(self._inherits_join_calc(self._table, f, query),f))

        for f in selection_fields:
            if f == 'gender':
                select_terms.append(u"array_to_string(ARRAY_AGG(DISTINCT (CASE %s WHEN 'nam' THEN 'Nam' WHEN 'nu' THEN 'Nữ' END)),', ') AS %s " %(self._inherits_join_calc(self._table, f, query),f))
            elif f == 'enter_source':
                select_terms.append(
                    u"ARRAY_AGG(DISTINCT (CASE %s WHEN '1' THEN 'Ngắn hạn' WHEN '2' THEN 'Dài hạn' WHEN '3' THEN 'Ban chỉ đạo' ELSE '' END)) AS %s " % (
                    self._inherits_join_calc(self._table, f, query), f))
        #
        # for f in many2one_fields:
        #     _logger.info("AAA %s"%self._fields[f].comodel_name)

        for f in many2one_fields:
            if f == 'dispatchcom':
                select_terms.append(u"(SELECT name_short from %s WHERE %s.id = min(%s)) AS %s" %(self._fields[f].comodel_name.replace(".", "_"),self._fields[f].comodel_name.replace(".", "_"),self._inherits_join_calc(self._table, f, query),f))
            else:
                select_terms.append(u"(SELECT name from %s WHERE %s.id = min(%s)) AS %s" % (
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
        return self.fields_get(allfields, attributes)
