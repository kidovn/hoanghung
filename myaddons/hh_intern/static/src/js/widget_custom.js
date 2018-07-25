odoo.define('hh_intern.WidgetCustom', function (require) {
    "use strict";
    var core = require('web.core');
    var session = require('web.session');
    var common = require('web.form_common');
    var QWeb = core.qweb;
    var list_widget_registry = core.list_widget_registry;
    var _t = core._t;
    var pyeval = require('web.pyeval');


    var Column = list_widget_registry.get('field');

    Column.include({
        init:function(){
            this._super.apply(this, arguments);
            this.options_tmp = pyeval.py_eval(this.options|| '{}');
        }

    });

    var ColumnOne2Many = Column.extend({
        init:function(){
            this._super.apply(this, arguments);
        },
        _format: function (row_data, options) {

            return _.escape(_.str.sprintf(_t("(%d records)"), row_data[this.id].value.length));
//            return _.str.sprintf('<span class="o_one2many_col">%s</span>',tmp);
        }

    });

    var ColumnIntegerCustom = Column.extend({
        _format: function (row_data, options) {
            if (!_.isEmpty(row_data[this.id].value)) {
                // If value, use __display version for printing
                if (!!row_data[this.id + '__display']) {
                    row_data[this.id] = row_data[this.id + '__display'];
                } else {
                    row_data[this.id] = {'value': ''};
                }
            }
            return this._super(row_data, options);
//            return _.str.sprintf('<span class="o_one2many_col">%s</span>',tmp);
        }

    });

    var ColumnBoolButton = list_widget_registry.get('field.boolean').extend({
        init: function(){
            this._super.apply(this, arguments);
        },

        format: function (row_data, options) {
            if(options.options && options.options.deletable && row_data[this.id] && !row_data[this.id].value){
                return _.str.sprintf('<div class="o_bool_button"><button style="font-size:8px" class="btn btn-primary btn-sm">%s</div>',
                         this.options_tmp["terminology"].action_false);
            }
            else{
                if(row_data[this.id] && row_data[this.id].value)
                    return _.str.sprintf('<span class="o_stat_text o_not_hover text-success">%s</span>',this.options_tmp["terminology"].string_true);
                else
                    return _.str.sprintf('<span class="o_stat_text o_not_hover text-danger">%s</span>',this.options_tmp["terminology"].string_false);
            }
        }

    });



    var ColumnBoolButtonReverse = list_widget_registry.get('field.boolean').extend({
        init: function(){
            this._super.apply(this, arguments);
        },

        format: function (row_data, options) {
            if(options.options && options.options.deletable && row_data[this.id].value){
                return _.str.sprintf('<div class="o_bool_button_reverse"><button style="font-size:8px" class="btn btn-primary btn-sm">%s</div>',
                         this.options_tmp["terminology"].action_true);
            }
            else{
                if(row_data[this.id].value)
                    return _.str.sprintf('<span class="o_stat_text o_not_hover text-success">%s</span>',this.options_tmp["terminology"].string_true);
                else
                    return _.str.sprintf('<span class="o_stat_text o_not_hover text-danger">%s</span>',this.options_tmp["terminology"].string_false);
            }
        }

    });

    var ColumnBoolDelete = list_widget_registry.get('field.boolean').extend({
        init: function(){
            this._super.apply(this, arguments);
        },

        format: function (row_data, options) {
            if(options.options && options.options.deletable && row_data[this.id].value){
                return '<span name="delete" class="fa fa-trash-o bool_delete"/>';
            }
            else{
                return "";
            }
        }

    });

    var ColumnToggleButton = list_widget_registry.get('field.boolean').extend({
        init: function(){
            this._super.apply(this, arguments);
        },

        format: function (row_data, options) {
            if(options.options && options.options.deletable){
                return _.str.sprintf('<div class="%s"><button style="font-size:8px" class="btn %s btn-sm">%s</div>',
                         row_data[this.id].value ? 'o_bool_button_reverse':'o_bool_button',row_data[this.id].value ? 'btn_toggle':'btn-primary',
                         row_data[this.id].value ? this.options_tmp["terminology"].action_false: this.options_tmp["terminology"].action_true);
            }
            else{
                if(row_data[this.id].value)
                    return _.str.sprintf('<span class="o_stat_text o_not_hover text-success">%s</span>',this.options_tmp["terminology"].string_true);
                else
                    return _.str.sprintf('<span class="o_stat_text o_not_hover text-danger">%s</span>','');
            }
        }

    });

    var ColumnToggleButtonExtend = list_widget_registry.get('field.boolean').extend({
        init: function(){
            this._super.apply(this, arguments);
        },

        format: function (row_data, options) {
            if(options.options && options.options.deletable){
                return _.str.sprintf('<div class="%s"><button style="font-size:8px" class="btn %s btn-sm">%s</div>',
                         row_data[this.id].value ? 'o_bool_button_reverse':'o_bool_button_extend',row_data[this.id].value ? 'btn_toggle':'btn-primary',
                         row_data[this.id].value ? this.options_tmp["terminology"].action_false: this.options_tmp["terminology"].action_true);
            }
            else{
                if(row_data[this.id].value)
                    return _.str.sprintf('<span class="o_stat_text o_not_hover text-success">%s</span>',this.options_tmp["terminology"].string_true);
                else
                    return _.str.sprintf('<span class="o_stat_text o_not_hover text-danger">%s</span>','');
            }
        }

    });

    var ColumnColor = Column.extend({
        /**
         * If password field, only display replacement characters (if value is
         * non-empty)
         */
         get_value:function(row_data){
            var value = row_data[this.id].value;
            if (value){
                return 'background:'+value;
            }
            else{
                return '';
            }

        },
        _format: function (row_data, options) {
            return '<div style="height:20px;width:100%;'+this.get_value(row_data)+'"></div>';
        },
    });


    var FieldBooleanDelete = common.AbstractField.extend({
        init: function() {
            this._super.apply(this, arguments);
        },

        render_value: function() {
            this._super();
            this.$el.html("");
        },

    });

    var FieldBooleanButton = common.AbstractField.extend({
        className: 'o_stat_info',
        init: function() {
            this._super.apply(this, arguments);
            switch (this.options["terminology"]) {
                case "active":
                    this.string_true = _t("Active");
                    this.hover_true = _t("Deactivate");
                    this.string_false = _t("Inactive");
                    this.hover_false = _t("Activate");
                    break;
                case "archive":
                    this.string_true = _t("Active");
                    this.hover_true = _t("Archive");
                    this.string_false = _t("Archived");
                    this.hover_false = _t("Unarchive");
                    break;
                default:
                    var terms = typeof this.options["terminology"] === 'string' ? {} : this.options["terminology"];
                    this.string_true = _t(terms.string_true || "On");
                    this.hover_true = _t(terms.hover_true || terms.string_false || "Switch Off");
                    this.string_false = _t(terms.string_false || "Off");
                    this.hover_false = _t(terms.hover_false || terms.string_true || "Switch On");
            }
        },

        render_value: function() {
            this._super();
            this.$el.html(QWeb.render("MyBoolButton", {widget: this}));
        },
        is_false: function() {
            return false;
        },
    });

    var FieldBooleanButtonReverse = common.AbstractField.extend({
        className: 'o_stat_info',
        init: function() {
            this._super.apply(this, arguments);
            var terms = typeof this.options["terminology"] === 'string' ? {} : this.options["terminology"];
            this.string_true = _t(terms.string_true || "On");
            this.hover_true = _t(terms.hover_true || terms.string_false || "Switch Off");
            this.string_false = _t(terms.string_false || "Off");
            this.hover_false = _t(terms.hover_false || terms.string_true || "Switch On");
        },
        render_value: function() {
            this._super();
            this.$el.html(QWeb.render("MyBoolButton", {widget: this}));
        },
        is_false: function() {
            return false;
        },
    });


    var ColorWidget = common.AbstractField.extend({
        template: 'ColorWidget',
        start: function() {
            this._super();
            this.on("change:value", this, function() {
                this.render_value();
                this._toggle_label();
            });
        },

        get_value:function(){
            var value = this.get('value');
            if (value){
                return value;
            }
            else{
                return '#FFFFFF';
            }

        },

        render_value: function() {
//            this._super.apply(this, arguments);
//            this.$el.removeClass('o_form_field_empty');
            this.$el.empty();
            this.$el.html('<div style="height:20px;width:100%; background:'+this.get_value()+'"></div>')
        },
    });


    list_widget_registry.add('field.bool_button', ColumnBoolButton);
    list_widget_registry.add('field.bool_delete', ColumnBoolDelete);
    list_widget_registry.add('field.bool_button_reverse', ColumnBoolButtonReverse);
    list_widget_registry.add('field.bool_button_toggle', ColumnToggleButton);
    list_widget_registry.add('field.one2many_custom', ColumnOne2Many);

    list_widget_registry.add('field.integer_custom', ColumnIntegerCustom);
    list_widget_registry.add('field.bool_button_toggle_extend', ColumnToggleButtonExtend);

    list_widget_registry.add('field.color', ColumnColor);

    core.form_widget_registry.add('bool_button', FieldBooleanButton);
    core.form_widget_registry.add('bool_button_reverse', FieldBooleanButtonReverse);

    core.form_widget_registry.add('color_widget', ColorWidget);
//    core.form_widget_registry.add('bool_delete', FieldBooleanDelete);
});