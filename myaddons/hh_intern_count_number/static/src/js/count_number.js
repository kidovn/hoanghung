
odoo.define('hh_intern.ListViewNew', function (require) {
"use strict";
    var ControlPanel = require('web.ControlPanel');
    var core = require('web.core');
    var data = require('web.data');
    var Dialog = require('web.Dialog');
    var common = require('web.form_common');
    var ListView = require('web.ListView');
    require('web.ListEditor'); // one must be sure that the include of ListView are done (for eg: add start_edition methods)
    var Model = require('web.DataModel');
    var session = require('web.session');
    var utils = require('web.utils');
    var ViewManager = require('web.ViewManager');

    var _t = core._t;
    var QWeb = core.qweb;
    var COMMANDS = common.commands;
    var list_widget_registry = core.list_widget_registry;
    var One2ManyListView = core.one2many_view_registry.get('list');

//    ListView.include({
//        _template:'ListViewCount',
//        init: function() {
//        this._super.apply(this, arguments);
//        this.options = _.defaults(this.options, {
//            GroupsType: ListView.Groups,
//            ListType: ListView.List,
//        });
//    });

    var X2ManyListView = ListView.extend({
        _template:'ListViewCount',
        is_valid: function () {
            if (!this.fields_view || !this.editable()){
                return true;
            }
            if (_.isEmpty(this.records.records)){
                return true;
            }
            var fields = this.editor.form.fields;
            var current_values = {};
            _.each(fields, function(field){
                field._inhibit_on_change_flag = true;
                field.__no_rerender = field.no_rerender;
                field.no_rerender = true;
                current_values[field.name] = field.get('value');
            });
            var ids = _.map(this.records.records, function (item) { return item.attributes.id; });
            var cached_records = _.filter(this.dataset.cache, function(item){return _.contains(ids, item.id) && !_.isEmpty(item.values) && !item.to_delete;});
            var valid = _.every(cached_records, function(record){
                _.each(fields, function(field){
                    var value = record.values[field.name];
                    field._inhibit_on_change_flag = true;
                    field.no_rerender = true;
                    field.set_value(_.isArray(value) && _.isArray(value[0]) ? [COMMANDS.delete_all()].concat(value) : value);
                });
                return _.every(fields, function(field){
                    field.process_modifiers();
                    field._check_css_flags();
                    return field.is_valid();
                });
            });
            _.each(fields, function(field){
                field.set('value', current_values[field.name], {silent: true});
                field._inhibit_on_change_flag = false;
                field.no_rerender = field.__no_rerender;
            });
            return valid;
        },
        render_pager: function($node, options) {
            options = _.extend(options || {}, {
                single_page_hidden: true,
            });
            this._super($node, options);
        },
        display_nocontent_helper: function () {
            return false;
        },
    });

    var X2ManyList = ListView.List.extend({
        init: function (){
            this._super.apply(this, arguments);
        },
        render: function () {
            var self = this;
            this.$current.html(
                QWeb.render('ListViewCount.rows', _.extend({}, this, {
                        render_cell: function () {
                            return self.render_cell.apply(self, arguments); }
                    })));
            this.pad_table_to(4);
        },

        pad_table_to_tmp: function (count) {
            if (this.records.length >= count ||
                    _(this.columns).any(function(column) { return column.meta; })) {
                return;
            }
            var cells = [];
            cells.push('<td class="stt"></td>');
            if (this.options.selectable) {
                cells.push('<td class="o_list_record_selector"></td>');
            }
            _(this.columns).each(function(column) {
                if (column.invisible === '1') {
                    return;
                }
                cells.push('<td title="' + column.string + '">&nbsp;</td>');
            });
            if (this.options.deletable) {
                cells.push('<td class="o_list_record_delete"></td>');
            }
            cells.unshift('<tr>');
            cells.push('</tr>');

            var row = cells.join('');
            this.$current
                .children('tr:not([data-id])').remove().end()
                .append(new Array(count - this.records.length + 1).join(row));
        },

        pad_table_to: function (count) {
            if (!this.view.is_action_enabled('create') || this.view.x2m.get('effective_readonly')) {
                if (this.records.length >= count ||
                    _(this.columns).any(function(column) { return column.meta; })) {
                    return;
                }
                var cells = [];
                cells.push('<td class="stt"/>');
                if (this.options.selectable) {
                    cells.push('<td class="o_list_record_selector"></td>');
                }
                _(this.columns).each(function(column) {
                    if (column.invisible === '1') {
                        return;
                    }
                    cells.push('<td title="' + column.string + '">&nbsp;</td>');
                });
                if (this.options.deletable) {
                    cells.push('<td class="o_list_record_delete"></td>');
                }
                cells.unshift('<tr>');
                cells.push('</tr>');

                var row = cells.join('');
                this.$current
                    .children('tr:not([data-id])').remove().end()
                    .append(new Array(count - this.records.length + 1).join(row));
                return;
            }

            this.pad_table_to_tmp(count > 0 ? count - 1 : 0);

            var self = this;
            var columns = _(this.columns).filter(function (column) {
                return column.invisible !== '1';
            }).length;
            if (this.options.selectable) { columns++; }
            if (this.options.deletable) { columns++; }

            columns++;//stt

            var $cell = $('<td>', {
                colspan: columns,
                'class': 'o_form_field_x2many_list_row_add'
            }).append(
                $('<a>', {href: '#'}).text(_t("Add an item"))
                    .click(function (e) {
                        e.preventDefault();
                        e.stopPropagation();
                        var def;
                        if (self.view.editable()) {
                            // FIXME: there should also be an API for that one
                            if (self.view.editor.form.__blur_timeout) {
                                clearTimeout(self.view.editor.form.__blur_timeout);
                                self.view.editor.form.__blur_timeout = false;
                            }
                            def = self.view.save_edition();
                        }
                        $.when(def).done(self.view.do_add_record.bind(self));
                    }));

            var $padding = this.$current.find('tr:not([data-id]):first');
            var $newrow = $('<tr>').append($cell);
            if ($padding.length) {
                $padding.before($newrow);
            } else {
                this.$current.append($newrow);
            }
        },
        render_record: function (record) {
            var self = this;
            var index = this.records.indexOf(record);
            return QWeb.render('ListViewCount.row', {
                columns: this.columns,
                options: this.options,
                record: record,
                row_parity: (index % 2 === 0) ? 'even' : 'odd',
                counter:index+1,
                view: this.view,
                render_cell: function () {
                    return self.render_cell.apply(self, arguments); }
            });
        },

    });

    var Many2ManyListView = X2ManyListView.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.options = _.extend(this.options, {
                ListType: X2ManyList,
            });
            this.on('edit:after', this, this.proxy('_after_edit'));
            this.on('save:before cancel:before', this, this.proxy('_before_unedit'));
        },
        do_add_record: function () {
            var self = this;

            new common.SelectCreateDialog(this, {
                res_model: this.model,
                domain: new data.CompoundDomain(this.x2m.build_domain(), ["!", ["id", "in", this.x2m.dataset.ids]]),
                context: this.x2m.build_context(),
                title: _t("Add: ") + this.x2m.string,
                alternative_form_view: this.x2m.field.views ? this.x2m.field.views.form : undefined,
                no_create: this.x2m.options.no_create || !this.is_action_enabled('create'),
                on_selected: function(element_ids) {
                    return self.x2m.data_link_multi(element_ids).then(function() {
                        if ('sequence_pass' in self.fields_view.fields){
                            var smallest = 1;
                            _.each(self.x2m.dataset.ids, function(id){
                                self.x2m.dataset.read_ids([id],['sequence_pass'],{}).then(function (records) {
                                    if(records[0].sequence_pass>smallest){
                                        smallest = records[0].sequence_pass;
                                    }
                                });
                            });
                            _.each(element_ids, function (id) {
                                    smallest = smallest+1;
                                    self.x2m.dataset._update_cache(id,{'changes':{'sequence_pass':smallest}});
                                }
                            );
                        }
                        else if ('sequence' in self.fields_view.fields){
                            var smallest = 1;
                            _.each(self.x2m.dataset.ids, function(id){
                                self.x2m.dataset.read_ids([id],['sequence'],{}).then(function (records) {
                                    if(records[0].sequence_pass>smallest){
                                        smallest = records[0].sequence_pass;
                                    }
                                });
                            });
                            _.each(element_ids, function (id) {
                                    smallest = smallest+1;
                                    self.x2m.dataset._update_cache(id,{'changes':{'sequence':smallest}});
                                }
                            );
                        }

                        self.x2m.reload_current_view();
                    });
                }
            }).open();
        },
        do_activate_record: function(index, id) {
            var self = this;
            var pop = new common.FormViewDialog(this, {
                res_model: this.model,
                res_id: id,
                context: this.x2m.build_context(),
                title: _t("Open: ") + this.x2m.string,
                alternative_form_view: this.x2m.field.views ? this.x2m.field.views.form : undefined,
                readonly: !this.is_action_enabled('edit') || self.x2m.get("effective_readonly"),
            }).open();
            pop.on('write_completed', self, function () {
                self.dataset.evict_record(id);
                self.reload_content();
            });
        },
        do_button_action: function(name, id, callback) {
            var self = this;
            var _sup = _.bind(this._super, this);
            if (! this.x2m.options.reload_on_button) {
                return _sup(name, id, callback);
            } else {
                return this.x2m.view.save().then(function() {
                    return _sup(name, id, function() {
                        self.x2m.view.reload();
                    });
                });
            }
        },
        _after_edit: function () {
            this.editor.form.on('blurred', this, this._on_blur_many2many);
        },
        _before_unedit: function () {
            this.editor.form.off('blurred', this, this._on_blur_many2many);
        },
        _on_blur_many2many: function() {
            return this.save_edition().done(function () {
                if (self._dataset_changed) {
                    self.dataset.trigger('dataset_changed');
                }
            });
        },

    });

    var FieldMany2Many = core.form_widget_registry.get('many2many').extend({
        init: function() {
            this._super.apply(this, arguments);
            this.x2many_views = {
                list: Many2ManyListView,
                kanban: core.view_registry.get('many2many_kanban'),
            };
        },


    });

    var One2ManyListViewNew  = One2ManyListView.extend({
        _template:'ListViewCount',
        init: function () {
            this._super.apply(this, arguments);
            this.options = _.extend(this.options, {
                ListType: X2ManyList
            });

        },
    });

    var FieldOne2Many = core.form_widget_registry.get('one2many').extend({
        init: function() {
            this._super.apply(this, arguments);
            this.x2many_views = {
                kanban: core.view_registry.get('one2many_kanban'),
                list: One2ManyListViewNew,
            };
        },

//        send_commands: function (command_list, options) {
//            var self = this;
//            var def = $.Deferred();
//            var dataset = this.dataset;
//            var res = true;
//            options = options || {};
//            var internal_options = _.extend({}, options, {'internal_dataset_changed': true});
//
//            _.each(command_list, function(command) {
//                self.mutex.exec(function() {
//                    var id = command[1];
//                    switch (command[0]) {
//                        case COMMANDS.CREATE:
//                            var data = _.clone(command[2]);
//                            delete data.id;
//                            return dataset.create(data, internal_options).then(function (id) {
//                                dataset.ids.push(id);
//                                res = id;
//                            });
//                        case COMMANDS.UPDATE:
//                            return dataset.write(id, command[2], internal_options).then(function () {
//                                if (dataset.ids.indexOf(id) === -1) {
//                                    dataset.ids.push(id);
//                                    res = id;
//                                }
//                            });
//                        case COMMANDS.FORGET:
//                            return dataset.unlink([id]);
//                        case COMMANDS.DELETE:
//                            return dataset.unlink([id]);
//                        case COMMANDS.LINK_TO:
//                            if (dataset.ids.indexOf(id) === -1) {
//                                return dataset.add_ids([id], internal_options);
//                            }
//                            return;
//                        case COMMANDS.DELETE_ALL:
//                            return dataset.reset_ids([], {keep_read_data: true});
//                        case COMMANDS.REPLACE_WITH:
//                            dataset.ids = [];
//                            return dataset.alter_ids(command[2], internal_options);
//                        default:
//                            throw new Error("send_commands to '"+self.name+"' receive a non command value." +
//                                "\n" + JSON.stringify(command_list));
//                    }
//                });
//            });
//
//            this.mutex.def.then(function () {
//                self.trigger("change:commands", options);
//                def.resolve(res);
//            });
//            return def;
//        },
    })

    core.form_widget_registry.add('many2many', FieldMany2Many).add('one2many',FieldOne2Many);

});