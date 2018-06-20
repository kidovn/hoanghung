# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

from odoo.exceptions import UserError


class IrFilters(models.Model):
    _inherit = 'ir.filters'

    # @api.model
    # @api.returns('self', lambda value: value.id)
    # def create_or_replace(self, vals):
    #     return super(IrFilters, self).create_or_replace(vals)
    #
    # @api.model
    # def _create(self, vals):
    #     # low-level implementation of create()
    #     if self.is_transient():
    #         self._transient_vacuum()
    #
    #     # data of parent records to create or update, by model
    #     tocreate = {
    #         parent_model: {'id': vals.pop(parent_field, None)}
    #         for parent_model, parent_field in self._inherits.iteritems()
    #     }
    #
    #     # list of column assignments defined as tuples like:
    #     #   (column_name, format_string, column_value)
    #     #   (column_name, sql_formula)
    #     # Those tuples will be used by the string formatting for the INSERT
    #     # statement below.
    #     updates = [
    #         ('id', "nextval('%s')" % self._sequence),
    #     ]
    #
    #     upd_todo = []
    #     unknown_fields = []
    #     protected_fields = []
    #     for name, val in vals.items():
    #         field = self._fields.get(name)
    #         if not field:
    #             unknown_fields.append(name)
    #             del vals[name]
    #         elif field.inherited:
    #             tocreate[field.related_field.model_name][name] = val
    #             del vals[name]
    #         elif not field.store:
    #             del vals[name]
    #         elif field.inverse:
    #             protected_fields.append(field)
    #     if unknown_fields:
    #         _logger.warning('No such field(s) in model %s: %s.', self._name, ', '.join(unknown_fields))
    #
    #     # create or update parent records
    #     for parent_model, parent_vals in tocreate.iteritems():
    #         parent_id = parent_vals.pop('id')
    #         if not parent_id:
    #             parent_id = self.env[parent_model].create(parent_vals).id
    #         else:
    #             self.env[parent_model].browse(parent_id).write(parent_vals)
    #         updates.append((self._inherits[parent_model], '%s', parent_id))
    #
    #     # set boolean fields to False by default (to make search more powerful)
    #     for name, field in self._fields.iteritems():
    #         if field.type == 'boolean' and field.store and name not in vals:
    #             vals[name] = False
    #
    #     # determine SQL values
    #     for name, val in vals.iteritems():
    #         field = self._fields[name]
    #         if field.store and field.column_type:
    #             tmp = field.convert_to_column(val, self)
    #             if name=='domain':
    #                 if 'time.strftime' in tmp:
    #                     tmp = tmp.replace('u\'time','time').replace('")\'','")')
    #             updates.append((name, field.column_format,tmp))
    #         else:
    #             upd_todo.append(name)
    #
    #         if hasattr(field, 'selection') and val:
    #             self._check_selection_field_value(name, val)
    #
    #     if self._log_access:
    #         updates.append(('create_uid', '%s', self._uid))
    #         updates.append(('write_uid', '%s', self._uid))
    #         updates.append(('create_date', "(now() at time zone 'UTC')"))
    #         updates.append(('write_date', "(now() at time zone 'UTC')"))
    #
    #     # insert a row for this record
    #     cr = self._cr
    #     query = """INSERT INTO "%s" (%s) VALUES(%s) RETURNING id""" % (
    #         self._table,
    #         ', '.join('"%s"' % u[0] for u in updates),
    #         ', '.join(u[1] for u in updates),
    #     )
    #     cr.execute(query, tuple(u[2] for u in updates if len(u) > 2))
    #
    #     # from now on, self is the new record
    #     id_new, = cr.fetchone()
    #     self = self.browse(id_new)
    #
    #     if self._parent_store and not self._context.get('defer_parent_store_computation'):
    #         if self.pool._init:
    #             self.pool._init_parent[self._name] = True
    #         else:
    #             parent_val = vals.get(self._parent_name)
    #             if parent_val:
    #                 # determine parent_left: it comes right after the
    #                 # parent_right of its closest left sibling
    #                 pleft = None
    #                 cr.execute("SELECT parent_right FROM %s WHERE %s=%%s ORDER BY %s" % \
    #                            (self._table, self._parent_name, self._parent_order),
    #                            (parent_val,))
    #                 for (pright,) in cr.fetchall():
    #                     if not pright:
    #                         break
    #                     pleft = pright + 1
    #                 if not pleft:
    #                     # this is the leftmost child of its parent
    #                     cr.execute("SELECT parent_left FROM %s WHERE id=%%s" % self._table, (parent_val,))
    #                     pleft = cr.fetchone()[0] + 1
    #             else:
    #                 # determine parent_left: it comes after all top-level parent_right
    #                 cr.execute("SELECT MAX(parent_right) FROM %s" % self._table)
    #                 pleft = (cr.fetchone()[0] or 0) + 1
    #
    #             # make some room for the new node, and insert it in the MPTT
    #             cr.execute("UPDATE %s SET parent_left=parent_left+2 WHERE parent_left>=%%s" % self._table,
    #                        (pleft,))
    #             cr.execute("UPDATE %s SET parent_right=parent_right+2 WHERE parent_right>=%%s" % self._table,
    #                        (pleft,))
    #             cr.execute("UPDATE %s SET parent_left=%%s, parent_right=%%s WHERE id=%%s" % self._table,
    #                        (pleft, pleft + 1, id_new))
    #             self.invalidate_cache(['parent_left', 'parent_right'])
    #
    #     with self.env.protecting(protected_fields, self):
    #         # invalidate and mark new-style fields to recompute; do this before
    #         # setting other fields, because it can require the value of computed
    #         # fields, e.g., a one2many checking constraints on records
    #         self.modified(self._fields)
    #
    #         # defaults in context must be removed when call a one2many or many2many
    #         rel_context = {key: val
    #                        for key, val in self._context.iteritems()
    #                        if not key.startswith('default_')}
    #
    #         # call the 'write' method of fields which are not columns
    #         for name in upd_todo:
    #             field = self._fields[name]
    #             field.write(self.with_context(rel_context), vals[name])
    #
    #         # for recomputing new-style fields
    #         self.modified(upd_todo)
    #
    #         # check Python constraints
    #         self._validate_fields(vals)
    #
    #         if self.env.recompute and self._context.get('recompute', True):
    #             # recompute new-style fields
    #             self.recompute()
    #
    #     self.check_access_rule('create')
    #
    #     if self.env.lang and self.env.lang != 'en_US':
    #         # add translations for self.env.lang
    #         for name, val in vals.iteritems():
    #             field = self._fields[name]
    #             if field.store and field.column_type and field.translate is True:
    #                 tname = "%s,%s" % (self._name, name)
    #                 self.env['ir.translation']._set_ids(tname, 'model', self.env.lang, self.ids, val, val)
    #
    #     self.create_workflow()
    #     return id_new