odoo.define('hh_hoso.search_filters', function (require) {
"use strict";

var core = require('web.core');
var datepicker = require('web.datepicker');
var formats = require('web.formats');
var Widget = require('web.Widget');

var _t = core._t;
var _lt = core._lt;

var ExtendedSearchProposition = Widget.extend(/** @lends instance.web.search.ExtendedSearchProposition# */{
    template: 'hh_hoso.extended_search.proposition',
    events: {
        'change .o_searchview_extended_prop_field': 'changed',
        'change .o_searchview_extended_prop_op': 'operator_changed',
        'click .o_searchview_extended_delete_prop': function (e) {
            e.stopPropagation();
            this.getParent().remove_proposition(this);
        },
    },
    /**
     * @constructs instance.web.search.ExtendedSearchProposition
     * @extends instance.web.Widget
     *
     * @param parent
     * @param fields
     */
    init: function (parent, field) {
        this._super(parent);
        this.field=field;
        this.attrs = {_: _, /*fields: {this.field},*/ selected: null};
        this.value = null;
//        this.select_field(field);
    },
    start: function () {
        return this._super().done(this.proxy('changed'));
    },
    changed: function() {
//        var nval = this.$(".o_searchview_extended_prop_field").val();
//        if(this.attrs.selected === null || this.attrs.selected === undefined || nval != this.attrs.selected.name) {
//            this.select_field(_.detect([this.field], function(x) {return x.name == nval;}));
//        }
        this.select_field(this.field);
    },
    operator_changed: function (e) {
        this.value.show_inputs($(e.target));
    },
    /**
     * Selects the provided field object
     *
     * @param field a field descriptor object (as returned by fields_get, augmented by the field name)
     */
    select_field: function(field) {
        var self = this;
        if(this.attrs.selected !== null && this.attrs.selected !== undefined) {
            this.value.destroy();
            this.value = null;
            this.$('.o_searchview_extended_prop_op').html('');
        }
        this.attrs.selected = field;
        if(field === null || field === undefined) {
            return;
        }

        var type = field.type;
        var Field = core.search_filters_registry.get_any([type, "char"]);

        this.value = new Field(this, field);
        _.each(this.value.operators, function(operator) {
            $('<option>', {value: operator.value})
                .text(String(operator.text))
                .appendTo(self.$('.o_searchview_extended_prop_op'));
        });
        var $value_loc = this.$('.o_searchview_extended_prop_value').show().empty();
        this.value.appendTo($value_loc);

    },
    get_filter: function () {
        if (this.attrs.selected === null || this.attrs.selected === undefined)
            return null;
        var field = this.attrs.selected,
            op_select = this.$('.o_searchview_extended_prop_op')[0],
            operator = op_select.options[op_select.selectedIndex];

        return {
            attrs: {
                domain: this.value.get_domain(field, operator),
                string: this.value.get_label(field, operator),
            },
            children: [],
            tag: 'filter',
        };
    },
});


var FilterGroup = Widget.extend(/** @lends instance.web.search.FilterGroup# */{
    template: 'hh_hoso.promosition',
//    icon: "fa-filter",
//    completion_label: _lt("Filter on: %s"),
    events: {
        'click .o_searchview_extended_delete_prop': function (e) {
            var parent = this.getParent();
            parent.remove_filter(this);
        },
    },
    init: function (filters,parent){
        this._super(parent);
        this.filters = filters;
    },

    start: function () {
//        this.$el.on('click', 'a', this.proxy('toggle_filter'));
        return $.when(null);
    },
});



return {
    ExtendedSearchProposition: ExtendedSearchProposition,
    FilterGroup: FilterGroup
};

});


odoo.define('hh_hoso.FilterMenu', function (require) {
"use strict";

var data_manager = require('web.data_manager');
var search_filters = require('hh_hoso.search_filters');
var search_inputs = require('web.search_inputs');
var Widget = require('web.Widget');

var core = require('web.core');
var _t = core._t;

return Widget.extend({
    template: 'hh_hoso.filter_field',
    events: {
        'click .o_add_filter': function (event) {
            event.preventDefault();
            this.toggle_custom_filter_menu();
        },
        'click li': function (event) {
            event.preventDefault();
            event.stopImmediatePropagation();
        },
        'hidden.bs.dropdown': function () {
            this.toggle_custom_filter_menu(false);
        },
        'click .o_add_condition': 'append_proposition',
        'click .o_apply_filter': 'commit_search',
        'keyup .o_searchview_extended_prop_value': function (ev) {
            if (ev.which === $.ui.keyCode.ENTER) {
                this.commit_search();
            }
        },

    },
    init: function (parent, data_field, filters) {
        this._super(parent);
        this.filters = filters || [];

        this.propositions = [];
        this.custom_filters_open = false;
        this.data_field = data_field;
        this.filters_group = [];
    },
    start: function () {
        var self = this;
        this.$menu = this.$('.o_filters_menu');
        this.$add_filter = this.$('.o_add_filter');
        this.$apply_filter = this.$('.o_apply_filter');
        this.$add_filter_menu = this.$('.o_add_filter_menu');
        _.each(this.filters, function (group) {
            if (group.is_visible()) {
                group.insertBefore(self.$add_filter);
                $('<li class="divider">').insertBefore(self.$add_filter);
            }
        });
    },

    add_filter: function(filters_expression){
        var filters = [{attrs: {
                domain: [filters_expression],
                string: this.get_label(this.data_field.string, filters_expression[1],filters_expression[2]),
            },
            children: [],
            tag: 'filter',}];

        var filters_widgets = _.map(filters, function (filter) {
                return new search_inputs.Filter(filter, this);
            });
        var filter_group = new search_filters.FilterGroup(filters_widgets,this);
        filter_group.insertBefore(this.$add_filter);
        this.filters_group.push(filter_group)
    },

    get_label: function (field, operator, value) {
        var format;
        switch (operator) {
        case '!=':
            if (value==false){
                format=  _t('%(field)s is set');
            }
            else{
                format = _t('%(field)s %(operator)s "%(value)s"');
            }
            break;
        case '=':
            if (value==false){
                format= _t('%(field)s is not set');
            }
            else{
                format = _t('%(field)s %(operator)s "%(value)s"');
            }
            break;

        default: format = _t('%(field)s %(operator)s "%(value)s"'); break;
        }
        return this.format_label(format, field, operator, value);
    },

    format_label: function (format, pfield, poperator, pvalue) {
        return _.str.sprintf(format, {
            field: pfield,
            // According to spec, HTMLOptionElement#label should return
            // HTMLOptionElement#text when not defined/empty, but it does
            // not in older Webkit (between Safari 5.1.5 and Chrome 17) and
            // Gecko (pre Firefox 7) browsers, so we need a manual fallback
            // for those
            operator: poperator,
            value: pvalue
        });
    },

    toggle_custom_filter_menu: function (is_open) {
        var self = this;
        this.custom_filters_open = !_.isUndefined(is_open) ? is_open : !this.custom_filters_open;
        var def;
        if (this.custom_filters_open && !this.propositions.length) {
            def = this.append_proposition();
        }
        $.when(def).then(function () {
            self.$add_filter
                .toggleClass('o_closed_menu', !self.custom_filters_open)
                .toggleClass('o_open_menu', self.custom_filters_open);
            self.$add_filter_menu.toggle(self.custom_filters_open);
            self.$('.o_filter_condition').toggle(self.custom_filters_open);
        });
    },
    append_proposition: function () {
        var self = this;
//        return this.get_fields().then(function (fields) {
        var prop = new search_filters.ExtendedSearchProposition(self, this.data_field);
        self.propositions.push(prop);
        prop.insertBefore(self.$add_filter_menu);
        self.$apply_filter.prop('disabled', false);
        return prop;
//        });
    },
    remove_proposition: function (prop) {
        this.propositions = _.without(this.propositions, prop);
        if (!this.propositions.length) {
            this.$apply_filter.prop('disabled', true);
        }
        prop.destroy();
    },

    remove_filter: function(filter){
        var index = this.filters_group.indexOf(filter);

        if (index !== -1) {
            this.filters_group.splice(index, 1);
            filter.destroy();
        }

    },
    commit_search: function () {
        var filters = _.invoke(this.propositions, 'get_filter'),
            filters_widgets = _.map(filters, function (filter) {
                return new search_inputs.Filter(filter, this);
            });
//            filter_group = new search_inputs.FilterGroup(filters_widgets, this.searchview),
//            facets = filters_widgets.map(function (filter) {
//                return filter_group.make_facet([filter_group.make_value(filter)]);
//            }
//            );
//        filter_group.insertBefore(this.$add_filter);
        var filter_group = new search_filters.FilterGroup(filters_widgets,this);
        filter_group.insertBefore(this.$add_filter);
//        $('<li class="divider">').insertBefore(this.$add_filter);
//        this.searchview.query.add(facets, {silent: true});
//        this.searchview.query.trigger('reset');
//
        this.filters_group.push(filter_group)
        _.invoke(this.propositions, 'destroy');
        this.propositions = [];
        this.append_proposition();
        this.toggle_custom_filter_menu(false);
    },
});

});