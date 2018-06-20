odoo.define('hh_hoso.DynamicListView', function (require) {
"use strict";


var core = require('web.core');
var data = require('web.data');
var data_manager = require('web.data_manager');
var DataExport = require('web.DataExport');
var formats = require('web.formats');
var common = require('web.list_common');
var Pager = require('web.Pager');
var pyeval = require('web.pyeval');
var session = require('web.session');
var Sidebar = require('web.Sidebar');
var utils = require('web.utils');
var Model = require('web.DataModel');
var Widget = require('web.Widget');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');

var QWeb = core.qweb;
var Class = core.Class;
var _t = core._t;
var _lt = core._lt;
var list_widget_registry = core.list_widget_registry;

var DynamicListView = Widget.extend({
    _template: 'hh_hoso.DynamicListView',

    defaults: {
        action: {},
        pager:true,
        limit:80,
    },
    init: function(parent,model,domain,context, fields, fields_view, date_options) {
        var self = this;
        this._super(parent);
        this.domain = domain;
        this.fields_view = fields_view;
        this.columns = [];
        this.records = new common.Collection();
        this.fields = fields;
        this.dataset = new data.DataSetSearch(this, model,context,[]);
        this.date_options = date_options;
        this.options = _.defaults({}, options, this.defaults);
        this._limit = (this.options.limit ||
                       this.defaults.limit ||80);

        this.current_min = 1;

//        this.records.bind('change', function (event, record, key) {
//            if (!_(self.aggregate_columns).chain()
//                    .pluck('name').contains(key).value()) {
//                return;
//            }
//            self.compute_aggregates();
//        });

    },
    start: function () {
        this.reload_content();
    },

    set_scrollTop: function(scrollTop) {
        this.scrollTop = scrollTop;
    },
    get_scrollTop: function() {
        return this.scrollTop;
    },

    update_pager: function (size, current_min) {
//        this.dataset.ids = dataset.ids;
        // Not exactly clean
//        if (this.dataset._length !== undefined) {
//            this.dataset._length = dataset._length;
//        }
        if (this.pager && !this.grouped) {
            var new_state = { size: size, limit: this._limit };
            if (current_min) {
                new_state.current_min = current_min;
            }
            this.pager.update_state(new_state);
        }
    },
//
//    set_scrollTop: function(scrollTop) {
//        this.scrollTop = scrollTop;
//    },
//    get_scrollTop: function() {
//        return this.scrollTop;
//    }

    render_pager: function($node, options) {
        if (!this.pager && this.options.pager) {
            this.pager = new Pager(this, this.dataset.size(), 1, this._limit, options);
//            this.pager.appendTo($node || this.options.$pager);
            this.pager.on('pager_changed', this, function (new_state) {
                var self = this;
                var limit_changed = (this._limit !== new_state.limit);

                this._limit = new_state.limit;
                this.current_min = new_state.current_min;
                this.reload_content().then(function(){
                     if (!limit_changed) {
                        self.set_scrollTop(0);
                        self.trigger_up('scrollTo', {offset: 0});
                    }
                });
            });
        }
    },

    load_list: function() {
        var self = this,
            list = new DynamicListView.List(this, {
                columns: this.columns,
                dataset: this.dataset,
                records: this.records
            });
       framework.blockUI();
       return this.session.rpc(
            '/web/dataset/search_data_for_report',
            {
                model: this.dataset.model,
                fields: this.fields,
                domain: this.domain,
//                domain: pyeval.eval('domains',
//                    [this.dataset.domain]),
                date_options: this.date_options,
                context:{"lang":"en_US","tz":"Asia/Ho_Chi_Minh","uid":1,"params":{"action":174}}
            }).then(function(data){
                framework.unblockUI();
                if (self.records.length) {
                    self.records.reset(null, {silent: true});
                }
    //            if (!self.datagroup.openable) {
    //                // Update the main list view pager
//                    self.update_pager(data.length, self.current_min);
    //            }

                self.records.add(data.records, {silent: true});
                list.render();
                return list;
            });


//        var options = { offset: this.current_min - 1, limit: this._limit, context: {bin_size: true} };
//        return this.dataset.read_slice(this.fields, options).then(function (records) {
//                // FIXME: ignominious hacks, parents (aka form view) should not send two ListView#reload_content concurrently
//            if (self.records.length) {
//                self.records.reset(null, {silent: true});
//            }
////            if (!self.datagroup.openable) {
////                // Update the main list view pager
//                self.update_pager(self.dataset, self.current_min);
////            }
//
//            self.records.add(records, {silent: true});
//            list.render();
//            return list;
//        });
    },

    reload_content: function(){
        var reloaded = $.Deferred();
        var self = this;
        this.reload_table();
        reloaded.resolve();
        self.$el.html(QWeb.render(this._template, this));
        this.$el.addClass("o_list_view_scroll_new");
        self.$('.o_list_view').append(this.elements);
        return reloaded.promise();
    },

    reload_table: function () {
        var self = this;
        var $el = $('<tbody>');
        this.elements = [$el[0]];
        this.setup_columns(this.fields_view);
        this.load_list().then(function (list) {
//            self.children[null] = list;
            self.elements =
                [list.$current.replaceAll($el)[0]];
//                self.setup_resequence_rows(list, dataset);

        });

    },

    setup_columns: function (fields) {
        this.columns.splice(0, this.columns.length);
        this.columns.push.apply(this.columns,
            _(this.fields_view).map(function (field) {
//                var id = field.attrs.name;
                return for_(field.name, field, field);
        }));
//        if (grouped) {
//            this.columns.unshift(new ListView.MetaColumn('_group'));
//        }

//        this.visible_columns = _.filter(this.columns, function (column) {
//            return column.invisible !== '1';
//        });

//        this.aggregate_columns = _(this.visible_columns).invoke('to_aggregate');
    },

//
//    do_search: function (domain, context, group_by) {
//        var self = this;
//        this.dataset = new data.DataSetSearch(self, self.model.name, self.model.context(), self.model.domain());
//
//    }
});

DynamicListView.List = Class.extend({
    init: function(opts){
        var self = this;
        this.options = opts.options;
        this.columns = opts.columns;
        this.dataset = opts.dataset;
        this.records = opts.records;


        this.record_callbacks = {
            'reset': function () { return self.on_records_reset(); },
            'change': function (event, record, attribute, value, old_value) {
                var $row;
                if (attribute === 'id') {
                    if (old_value) {
                        throw new Error(_.str.sprintf( _t("Setting 'id' attribute on existing record %s"),
                            JSON.stringify(record.attributes) ));
                    }
                    self.dataset.add_ids([value], self.records.indexOf(record));
                    // Set id on new record
                    $row = self.$current.children('[data-id=false]');
                } else {
                    $row = self.$current.children(
                        '[data-id=' + record.get('id') + ']');
                }
                if ($row.length) {
                    var $newRow = $(self.render_record(record));
                    $newRow.find('.o_list_record_selector input').prop('checked', !!$row.find('.o_list_record_selector input').prop('checked'));
                    $row.replaceWith($newRow);
                }
            },
            'add': function (ev, records, record, index) {
                var $new_row = $(self.render_record(record));
                var id = record.get('id');
                if (id) { self.dataset.add_ids([id], index); }

                if (index === 0) {
                    $new_row.prependTo(self.$current);
                } else {
                    var previous_record = records.at(index-1),
                        $previous_sibling = self.$current.children(
                                '[data-id=' + previous_record.get('id') + ']');
                    $new_row.insertAfter($previous_sibling);
                }
            }
        };

        _(this.record_callbacks).each(function (callback, event) {
            this.records.bind(event, callback);
        }, this);

        this.$current = $('<tbody>');
    },

    on_records_reset: function () {
        _(this.record_callbacks).each(function (callback, event) {
            this.records.unbind(event, callback);
        }, this);
    },

    render_cell: function (record, column) {
        var value;
        if(column.type === 'reference') {
            value = record.get(column.id);
            var ref_match;
            // Ensure that value is in a reference "shape", otherwise we're
            // going to loop on performing name_get after we've resolved (and
            // set) a human-readable version. m2o does not have this issue
            // because the non-human-readable is just a number, where the
            // human-readable version is a pair
            if (value && (ref_match = /^([\w\.]+),(\d+)$/.exec(value))) {
                // reference values are in the shape "$model,$id" (as a
                // string), we need to split and name_get this pair in order
                // to get a correctly displayable value in the field
                var model = ref_match[1],
                    id = parseInt(ref_match[2], 10);
                new data.DataSet(this.view, model).name_get([id]).done(function(names) {
                    if (!names.length) { return; }
                    record.set(column.id + '__display', names[0][1]);
                });
            }
        } else if (column.type === 'many2one') {
            value = record.get(column.id);
            // m2o values are usually name_get formatted, [Number, String]
            // pairs, but in some cases only the id is provided. In these
            // cases, we need to perform a name_get call to fetch the actual
            // displayable value
            if (typeof value === 'number' || value instanceof Number) {
                // fetch the name, set it on the record (in the right field)
                // and let the various registered events handle refreshing the
                // row
                new data.DataSet(this.view, column.relation)
                        .name_get([value]).done(function (names) {
                    if (!names.length) { return; }
                    record.set(column.id, names[0]);
                });
            }
        } else if (column.type === 'many2many') {
            value = record.get(column.id);
            // non-resolved (string) m2m values are arrays
            if (value instanceof Array && !_.isEmpty(value)
                    && !record.get(column.id + '__display')) {
                var ids;
                // they come in two shapes:
                if (value[0] instanceof Array) {
                    _.each(value, function(command) {
                        switch (command[0]) {
                            case 4: ids.push(command[1]); break;
                            case 5: ids = []; break;
                            case 6: ids = command[2]; break;
                            default: throw new Error(_.str.sprintf( _t("Unknown m2m command %s"), command[0]));
                        }
                    });
                } else {
                    // 2. an array of ids
                    ids = value;
                }
                new Model(column.relation)
                    .call('name_get', [ids, this.dataset.get_context()]).done(function (names) {
                        // FIXME: nth horrible hack in this poor listview
                        record.set(column.id + '__display',
                                   _(names).pluck(1).join(', '));
                        record.set(column.id, ids);
                    });
                // temporary empty display name
                record.set(column.id + '__display', false);
            }
        }
        return column.format(record.toForm().data, {
            model: this.dataset.model,
            id: record.get('id')
        });
    },
    render: function () {
        var self = this;
        this.$current.html(
            QWeb.render('hh_hoso.DynamicListView.rows', _.extend({}, this, {
                    render_cell: function () {
                        return self.render_cell.apply(self, arguments); }
                })));
    },

    render_record: function (record) {
        var self = this;
        var index = this.records.indexOf(record);
        return QWeb.render('DynamicListView.row', {
            columns: this.columns,
            options: this.options,
            record: record,
            row_parity: (index % 2 === 0) ? 'even' : 'odd',
            view: this.view,
            render_cell: function () {
                return self.render_cell.apply(self, arguments); }
        });
    },
});

function for_ (id, field, node) {
    var description = _.extend({tag: "field"}, field, node.attrs);
    var tag = description.tag;
    var Type = list_widget_registry.get_any([
        tag + '.' + description.widget,
        tag + '.'+ description.type,
        tag
    ]);
    return new Type(id, node.tag, description);
}


return DynamicListView;


});