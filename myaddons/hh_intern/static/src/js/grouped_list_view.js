
odoo.define('hh_intern.GroupedListView', function (require) {
"use strict";

var ControlPanel = require('web.ControlPanel');
var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var common = require('web.form_common');
var ListView = require('web.ListView');

var _t = core._t;
var QWeb = core.qweb;
var FieldMany2Many = core.form_widget_registry.get('many2many');
var FormView = require('web.FormView');

var ListViewGrouped = ListView.include({

    init: function() {
        var self = this;
        this._super.apply(this, arguments);
        // Sort
        var a = ['enterprise'];
        var default_order = this.fields_view.arch.attrs.default_order;
        var unsorted = !this.dataset._sort.length;
        if (unsorted && default_order && !this.grouped) {
            this.dataset.set_sort(a.concat(default_order.split(',')));
        }
    },

});

var X2ManyList = ListView.List.extend({
    init: function (){
        this._super.apply(this, arguments);
//        this.options = _.extend(this.options, {
//            ListType: ListViewGrouped
//        });

    },
    render: function () {
        var self = this;

        this.$current.html(
            QWeb.render('ListViewGrouped.rows', _.extend({}, this, {
                    render_cell: function () {
                        return self.render_cell.apply(self, arguments); }
                })));
        this.pad_table_to(4);
    },

    pad_table_to: function (count) {
        if (!this.view.is_action_enabled('create') || this.view.x2m.get('effective_readonly')) {
            this._super(count);
            return;
        }

        this._super(count > 0 ? count - 1 : 0);

        var self = this;
        var columns = _(this.columns).filter(function (column) {
            return column.invisible !== '1';
        }).length;
        if (this.options.selectable) { columns++; }
        if (this.options.deletable) { columns++; }

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
                    $.when(def).done(

                    self.view.do_add_record.bind(self)

                    );
                }));

        var $padding = this.$current.find('tr:not([data-id]):first');
        var $newrow = $('<tr>').append($cell);
        if ($padding.length) {
            $padding.before($newrow);
        } else {
            this.$current.append($newrow);
        }
    },
});

var One2ManyListViewGrouped = core.one2many_view_registry.get('list').extend({
    init: function () {
        this._super.apply(this, arguments);
        this.options = _.extend(this.options, {
            ListType: X2ManyList
        });
    },

});

var FieldOne2ManyGrouped = core.form_widget_registry.get('one2many').extend({
    init: function() {
        this._super.apply(this, arguments);
        this.x2many_views = {
            kanban: core.view_registry.get('one2many_kanban'),
            list: One2ManyListViewGrouped,
        };
    },

});

core.form_widget_registry
    .add('one2manygrouped', FieldOne2ManyGrouped);

});