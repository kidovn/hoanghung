odoo.define('hh_intern.PivotView', function (require) {
"use strict";

var core = require('web.core');

var core = require('web.core');
var crash_manager = require('web.crash_manager');
var data_manager = require('web.data_manager');
var formats = require('web.formats');
var framework = require('web.framework');
var Model = require('web.DataModel');
var session = require('web.session');
var Sidebar = require('web.Sidebar');
var utils = require('web.utils');
var View = require('web.View');

var _lt = core._lt;
var _t = core._t;
var QWeb = core.qweb;

var PivotView = core.view_registry.get('pivot');

var PivotViewExtend = PivotView.extend({

    willStart: function () {
        var self = this;

        var fields_def = data_manager.load_fields_for_report(this.dataset);
        var xlwt_def = session.rpc('/web/pivot/check_xlwt').then(function(result) {
            self.xlwt_installed = result;
        });

        this.fields_view.arch.children.forEach(function (field) {
            var name = field.attrs.name;
            if (field.attrs.interval) {
                name += ':' + field.attrs.interval;
            }
            //noinspection FallThroughInSwitchStatementJS
            switch (field.attrs.type) {
            case 'measure':
                self.widgets.push(field.attrs.widget || "");
                self.active_measures.push(name);
                break;
            case 'col':
                self.initial_col_groupby.push(name);
                break;
            default:
                if ('operator' in field.attrs) {
                    self.active_measures.push(name);
                    break;
                }
            case 'row':
                self.initial_row_groupby.push(name);
            }
        });
        if ((!this.active_measures.length) || this.fields_view.arch.attrs.display_quantity) {
            this.active_measures.push('__count__');
        }

        return $.when(fields_def, xlwt_def,View.prototype.willStart).then(function (fields) {
            self.prepare_fields(fields);
            // add active measures to the measure list.  This is very rarely necessary, but it
            // can be useful if one is working with a functional field non stored, but in a
            // model with an overrided read_group method.  In this case, the pivot view could
            // work, and the measure should be allowed.  However, be careful if you define a
            // measure in your pivot view: non stored functional fields will probably not work
            // (their aggregate will always be 0).
            _.each(self.active_measures, function (m) {
                if (!(m in self.measures)) {
                    self.measures[m] = self.fields[m];
                }
            });
        });
    },

    render_buttons: function ($node) {
        if ($node) {
            var self = this;

            var context = {measures: _.pairs(_.omit(this.measures, '__count__'))};
            this.$buttons = $(QWeb.render('PivotViewExtend.buttons', context));
            this.$buttons.click(this.on_button_click.bind(this));
            this.active_measures.forEach(function (measure) {
                self.$buttons.find('li[data-field="' + measure + '"]').addClass('selected');
            });
            this.$buttons.find('button').tooltip();

            this.$buttons.appendTo($node);
        }
    },

    draw_rows: function ($tbody, rows) {
        var self = this,
            i, j, value, $row, $cell, $header,
            nbr_measures = this.active_measures.length,
            length = rows[0].values.length,
            display_total = this.main_col.width > 1;

        var groupby_labels = _.map(this.main_row.groupbys, function (gb) {
            return self.fields[gb.split(':')[0]].string;
        });
        var measure_types = this.active_measures.map(function (name) {
            return self.measures[name].type;
        });
        var widgets = this.widgets;
        for (i = 0; i < rows.length; i++) {
            $row = $('<tr>');
            $header = $('<td>')
                .text(rows[i].title)
                .data('id', rows[i].id)
                .css('padding-left', (5 + rows[i].indent * 30) + 'px')
                .addClass(rows[i].expanded ? 'o_pivot_header_cell_opened' : 'o_pivot_header_cell_closed');
            if (rows[i].indent > 0) $header.attr('title', groupby_labels[rows[i].indent - 1]);
            $header.appendTo($row);
            for (j = 0; j < length; j++) {
                value = this.custom_format(rows[i].expanded,i,rows[i].values[j], {type: measure_types[j % nbr_measures], widget: widgets[j % nbr_measures]});

                $cell = $('<td>')
                            .data('id', rows[i].id)
                            .data('col_id', rows[i].col_ids[Math.floor(j / nbr_measures)])
                            .toggleClass('o_empty', !value)
                            .text(value)
                            .addClass('o_pivot_cell_value text-right');
                if (((j >= length - this.active_measures.length) && display_total) || i === 0){
                    $cell.css('font-weight', 'bold');
                }
                $row.append($cell);

                $cell.toggleClass('hidden-xs', j < length - this.active_measures.length);
            }
            $tbody.append($row);
        }
    },

    download_table: function () {
        framework.blockUI();
        var nbr_measures = this.active_measures.length,
            headers = this.compute_headers(),
            measure_row = nbr_measures > 1 ? _.last(headers) : [],
            rows = this.compute_rows(),
            i, j, value;
        headers[0].splice(0,1);
        // process measure_row
        for (i = 0; i < measure_row.length; i++) {
            measure_row[i].measure = this.measures[measure_row[i].measure].string;
        }
        // process all rows
        var self = this;
        var measure_types = this.active_measures.map(function (name) {
            return self.measures[name].type;
        });
        var widgets = this.widgets;

        for (i =0, j, value; i < rows.length; i++) {
            for (j = 0; j < rows[i].values.length; j++) {
//                value = rows[i].values[j];
                value = this.custom_format(rows[i].expanded,i,rows[i].values[j], {type: measure_types[j % nbr_measures], widget: widgets[j % nbr_measures]});
                rows[i].values[j] = {
                    is_bold: (i === 0) || ((this.main_col.width > 1) && (j >= rows[i].values.length - nbr_measures)),
                    value:  (value === undefined) ? "" : value,
                };
            }
        }
        var table = {
            headers: _.initial(headers),
            measure_row: measure_row,
            rows: rows,
            nbr_measures: nbr_measures,
            title: this.title,
        };
        if(table.measure_row.length + 1 > 256) {
            c.show_message(_t("For Excel compatibility, data cannot be exported if there are more than 256 columns.\n\nTip: try to flip axis, filter further or reduce the number of measures."));
            return;
        }
        session.get_file({
            url: '/web/pivot/export_xls',
            data: {data: JSON.stringify(table)},
            complete: framework.unblockUI,
            error: crash_manager.rpc_error.bind(crash_manager)
        });
    },

    custom_format: function (expanded,row_index,value, descriptor, value_if_empty) {
        if ((descriptor.type == 'datetime'|| descriptor.type == 'date') && value instanceof Array){
            if(expanded || row_index == 0){
                return "";
            }
            else if (value.length>2){
                return value.length +" records";
            }
            return value.filter(v=>v!='').join(", ");
        }
        else if (descriptor.type == 'many2one' && typeof value === 'string'){
            if(expanded|| row_index == 0){
                return "";
            }
            return value;
        }
        else if (descriptor.type == 'selection' && value instanceof Array){
            if(expanded|| row_index == 0){
                return "";
            }
            return value.filter(v=>v!='').join(", ");
        }

        else if (descriptor.type == 'selection' && typeof value === 'string'){
            if(expanded|| row_index == 0){
                return "";
            }
            return value;
        }
        else if (typeof value==='string'){
            if(expanded || row_index == 0){
                return "";
            }
        }

        return formats.format_value(value, descriptor, value_if_empty);

    },

    prepare_fields: function (fields) {
        var self = this,
            groupable_types = ['many2one', 'char', 'boolean',
                               'selection', 'date', 'datetime'];
        this.fields = fields;
        _.each(fields, function (field, name) {
            if ((name !== 'id') && (name !== 'sequence_exam')&& (name !== 'sequence_pass')&& (field.store === true)) {
                if (field.type === 'integer' || field.type === 'float' || field.type === 'monetary') {
                    self.measures[name] = field;
                }
                if (_.contains(groupable_types, field.type)) {
                    self.groupable_fields[name] = field;
                }
            }
        });
        this.measures.__count__ = {string: _t("Số lượng"), type: "integer"};
    },


});


var GroupByMenu = require('web.GroupByMenu');
GroupByMenu.include({
    get_fields: function () {
        var self = this;
        if (!this._fields_def) {
            this._fields_def = data_manager.load_fields(this.searchview.dataset).then(function (fields) {
                var groupable_types = ['many2one', 'char', 'boolean', 'selection', 'date', 'datetime'];
                var filter_group_field = _.filter(fields, function (field, name) {
                    if (field.sortable && field.searchable && _.contains(groupable_types, field.type)) {
                        field.name = name;
                        return field;
                    }
                });
                self.groupable_fields = _.sortBy(filter_group_field, 'string');

                self.$menu.append(QWeb.render('GroupByMenuSelector', self));
                self.$add_group_menu = self.$('.o_add_group');
                self.$group_selector = self.$('.o_group_selector');
                self.$('.o_select_group').click(function () {
                    self.toggle_add_menu(false);
                    var field = self.$group_selector.find(':selected').data('name');
                    self.add_groupby_to_menu(field);
                });
            });
        }
        return this._fields_def;
    },
});


core.view_registry.add('pivot_extend', PivotViewExtend);

return PivotViewExtend;

});