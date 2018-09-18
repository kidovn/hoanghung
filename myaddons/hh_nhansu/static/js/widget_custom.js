odoo.define('hh_nhansu.WidgetCustom', function (require) {
    "use strict";
    var core = require('web.core');
    var session = require('web.session');
    var common = require('web.form_common');
    var QWeb = core.qweb;
    var list_widget_registry = core.list_widget_registry;
    var _t = core._t;
    var pyeval = require('web.pyeval');
    var formats = require('web.formats');

    var time = require('web.time');
    var Widget = require('web.Widget');


    var DateWidget = Widget.extend({
        template: "web.datepicker",
        type_of_date: "date",
        events: {
            'dp.change': 'change_datetime',
            'dp.show': 'set_datetime_default',
            'change .o_datepicker_input': 'change_datetime',
        },
        init: function(parent, options) {
            this._super.apply(this, arguments);

            var l10n = _t.database.parameters;

            this.name = parent.name;
            this.options = _.defaults(options || {}, {
                pickTime: this.type_of_date === 'datetime',
                useSeconds: this.type_of_date === 'datetime',
                startDate: moment({ y: 1900 }),
                endDate: moment().add(200, "y"),
                calendarWeeks: true,
                icons: {
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down'
                },
                language : moment.locale(),
                format : time.strftime_to_moment_format((this.type_of_date === 'datetime')? (l10n.date_format + ' ' + l10n.time_format) : l10n.date_format),
            });
        },
        start: function() {
            this.$input = this.$('input.o_datepicker_input');
//            this.$el.datetimepicker(this.options);
//            this.picker = this.$el.data('DateTimePicker');
            this.set_readonly(false);
            this.set_value(false);
        },
        set_value: function(value) {
            this.set({'value': value});
            this.$input.val((value)? this.format_client(value) : '');
//            this.picker.setValue(this.format_client(value));
        },
        get_value: function() {
            return this.get('value');
        },
        set_value_from_ui: function() {
            var value = this.$input.val() || false;
            this.set_value(this.parse_client(value));
        },
        set_readonly: function(readonly) {
            this.readonly = readonly;
            this.$input.prop('readonly', this.readonly);
        },
        is_valid: function() {
            var value = this.$input.val();
            if(value === "") {
                return true;
            } else {
                try {
                    this.parse_client(value);
                    return true;
                } catch(e) {
                    return false;
                }
            }
        },
        parse_client: function(v) {
            return formats.parse_value(v, {"widget": this.type_of_date});
        },
        format_client: function(v) {
            return formats.format_value(v, {"widget": this.type_of_date});
        },
        set_datetime_default: function() {
            //when opening datetimepicker the date and time by default should be the one from
            //the input field if any or the current day otherwise
            var value = moment().second(0);
            if(this.$input.val().length !== 0 && this.is_valid()) {
                value = this.$input.val();
            }

            // temporarily set pickTime to true to bypass datetimepicker hiding on setValue
            // see https://github.com/Eonasdan/bootstrap-datetimepicker/issues/603
//            var saved_picktime = this.picker.options.pickTime;
//            this.picker.options.pickTime = true;
//            this.picker.setValue(value);
//            this.picker.options.pickTime = saved_picktime;
        },
        change_datetime: function(e) {
            if(this.is_valid()) {
                this.set_value_from_ui();
                this.trigger("datetime_changed");
            }
        },
        commit_value: function() {
            this.change_datetime();
        },
        destroy: function() {
//            this.picker.destroy();
            this._super.apply(this, arguments);
        },
    });


   var FieldDateCustom = common.AbstractField.extend(common.ReinitializeFieldMixin, {
        tagName: "span",
        className: "o_form_field_date",
        build_widget: function() {
            return new DateWidget(this);
        },
        initialize_content: function() {
            if (this.datewidget) {
                this.datewidget.destroy();
                this.datewidget = undefined;
            }

            if (!this.get("effective_readonly")) {
                this.datewidget = this.build_widget();
                this.datewidget.on('datetime_changed', this, function() {
                    this.internal_set_value(this.datewidget.get_value());
                });

                var self = this;
                this.datewidget.appendTo('<div>').done(function() {
                    self.datewidget.$el.addClass(self.$el.attr('class'));
                    self.replaceElement(self.datewidget.$el);
                    self.datewidget.$input.addClass('o_form_input');
                    self.setupFocus(self.datewidget.$input);
                });
            }
        },
        render_value: function() {
            if (this.get("effective_readonly")) {
                this.$el.text(formats.format_value(this.get('value'), this, ''));
            } else {
                this.datewidget.set_value(this.get('value'));
            }
        },
        is_syntax_valid: function() {
            return this.get("effective_readonly") || !this.datewidget || this.datewidget.is_valid();
        },
        is_false: function() {
            return this.get('value') === '' || this._super();
        },
        focus: function() {
            if (!this.get("effective_readonly")) {
                return this.datewidget.$input.focus();
            }
            return false;
        },
    });


    core.form_widget_registry.add('datecustom', FieldDateCustom);

});