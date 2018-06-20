odoo.define('hh_intern.FormCustom', function (require) {
"use strict";

var common = require('web.form_common');
var core = require('web.core');
var crash_manager = require('web.crash_manager');
var data = require('web.data');
var Dialog = require('web.Dialog');
var FormRenderingEngine = require('web.FormRenderingEngine');
var Model = require('web.DataModel');
var Pager = require('web.Pager');
var Sidebar = require('web.Sidebar');
var utils = require('web.utils');
var View = require('web.View');
var data_manager = require('web.data_manager');

var _t = core._t;
var _lt = core._lt;
var QWeb = core.qweb;
var FormView = require('web.FormView');

var FormViewCustom = FormView.extend({

    init: function() {
        this._super.apply(this, arguments);
        this.default_value = this.options.default_value;
    },

    load_defaults: function () {
        var self = this;
        var keys = _.keys(this.fields_view.fields);
        if (keys.length) {
            return this.dataset.default_get(keys).then(function(r) {
                var record = _.clone(r);
                if(self.default_value)
                    Object.keys(self.default_value).forEach(function(key) { record[key] = self.default_value[key]; });
                self.trigger('load_record', record);
            });
        }
        return $.when().then(this.trigger.bind(this, 'load_record', {}));
    },

    do_show: function (options) {
        var self = this;
        options = options || {};
        this.$el.removeClass('oe_form_dirty');

        var shown = this.has_been_loaded;
        if (options.reload !== false) {
            shown = shown.then(function() {
                if (self.dataset.index === null) {
                    // null index means we should start a new record
                    return self.on_button_new();
                }
                var fields = _.keys(self.fields_view.fields);
                fields.push('display_name');
                fields.push('__last_update');

//                if(self.record){
//                    return self.trigger('load_record', self.record);
//                }

                return self.dataset.read_index(fields, {
                    context: { 'bin_size': true }
                }).then(function(r) {
                    self.trigger('load_record', r);
                });
            });
        }
        return $.when(shown, View.prototype.do_show.apply(this, arguments) ).then(function() {
            self._actualize_mode(options.mode || self.options.initial_mode);
            core.bus.trigger('form_view_shown', self);
        });
    },

});

var SelectCreateDialogCustom = common.SelectCreateDialog.extend({

    create_edit_record: function() {
        this.close();
        return new FormViewDialogCustom(this.__parentedParent, this.options).open();
    },

});


var FormViewDialogCustom = common.ViewDialog.extend({

    init: function(parent, options) {
        var self = this;

        var multi_select = !_.isNumber(options.res_id) && !options.disable_multiple_selection;
        var readonly = _.isNumber(options.res_id) && options.readonly;

        if(!options || !options.buttons) {
            options = options || {};
            options.buttons = [
                {text: (readonly ? _t("Close") : _t("Discard")), classes: "btn-default o_form_button_cancel", close: true, click: function() {
                    self.view_form.trigger('on_button_cancel');
                }}
            ];

            if(!readonly) {
                options.buttons.splice(0, 0, {text: _t("Save") + ((multi_select)? " " + _t(" & Close") : ""), classes: "btn-primary", click: function() {
                        self.view_form.onchanges_mutex.def.then(function() {
                            if (!self.view_form.warning_displayed) {
                                $.when(self.view_form.save()).done(function() {
                                    self.view_form.reload_mutex.exec(function() {
                                        self.trigger('record_saved');
                                        self.close();
                                    });
                                });
                            }
                        });
                    }
                });

                if(multi_select) {
                    options.buttons.splice(1, 0, {text: _t("Save & New"), classes: "btn-primary", click: function() {
                        $.when(self.view_form.save()).done(function() {
                            self.view_form.reload_mutex.exec(function() {
                                self.view_form.on_button_new();
                            });
                        });
                    }});
                }
            }
        }

        this._super(parent, options);
    },

    open: function() {
        var self = this;
        var _super = this._super.bind(this);
        this.init_dataset();

        if (this.res_id) {
            this.dataset.ids = [this.res_id];
            this.dataset.index = 0;
        } else {
            this.dataset.index = null;
        }
        var options = _.clone(this.options.form_view_options) || {};
        if (this.res_id !== null) {
            options.initial_mode = this.options.readonly ? "view" : "edit";
        }
        _.extend(options, {
            $buttons: this.$buttons,
        });
        var FormView = core.view_registry.get('form');
        var fields_view_def;
        if (this.options.alternative_form_view) {
            fields_view_def = $.when(this.options.alternative_form_view);
        } else {
            fields_view_def = data_manager.load_fields_view(this.dataset, this.options.view_id, 'form', false);
        }
        fields_view_def.then(function (fields_view) {
            options.default_value = self.options.default_value;

            self.view_form = new FormViewCustom(self, self.dataset, fields_view, options);
            var fragment = document.createDocumentFragment();
            self.view_form.appendTo(fragment).then(function () {
                self.view_form.do_show().then(function() {
                    _super().$el.append(fragment);
                    self.view_form.autofocus();
                });
            });
        });

        return this;
    },

});

FormView.include({
    _process_save: function(save_obj) {
        var self = this;
        var prepend_on_create = save_obj.prepend_on_create;
        var def_process_save = $.Deferred();
        try {
            var form_invalid = false,
                values = {},
                first_invalid_field = null,
                readonly_values = {},
                deferred = [];

            $.when.apply($, deferred).always(function () {

                _.each(self.fields, function (f) {
                    if (!f.is_valid()) {
                        form_invalid = true;
                        if (!first_invalid_field) {
                            first_invalid_field = f;
                        }
                    } else if (f.name !== 'id' && (!self.datarecord.id || f._dirty_flag)
                        && f.name!='interns_promoted' && f.name!='interns_confirm_exam'
                        && f.name!='interns_escape_exam' && f.name!='interns_pass_new'
                        && f.name!='interns_preparatory' && f.name!='interns_cancel_pass' && f.name!='interns_departure') {
                        // Special case 'id' field, do not save this field
                        // on 'create' : save all non readonly fields
                        // on 'edit' : save non readonly modified fields
                        if (!f.get("readonly")) {
                            values[f.name] = f.get_value(true);

//                            //KIDO
//                            if(f.name == 'interns'){
//                                values['intern_order'] = f.get_value_sequence();
//                            }
//                            else if (f.name == 'interns_pass'){
//                                values['intern_pass_order'] = f.get_value_sequence();
//                            }


                        } else {
                            readonly_values[f.name] = f.get_value(true);
                        }
                    }

                });

                // Heuristic to assign a proper sequence number for new records that
                // are added in a dataset containing other lines with existing sequence numbers
                if (!self.datarecord.id && self.fields.sequence &&
                    !_.has(values, 'sequence') && !_.isEmpty(self.dataset.cache)) {
                    // Find current max or min sequence (editable top/bottom)
                    var current = _[prepend_on_create ? "min" : "max"](
                        _.map(self.dataset.cache, function(o){return o.values.sequence})
                    );
                    values['sequence'] = prepend_on_create ? current - 1 : current + 1;
                }
                if (form_invalid) {
                    self.set({'display_invalid_fields': true});
                    first_invalid_field.focus();
                    self.on_invalid();
                    def_process_save.reject();
                } else {
                    self.set({'display_invalid_fields': false});
                    var save_deferral;
                    if (!self.datarecord.id) {
                        // Creation save
                        save_deferral = self.dataset.create(values, {readonly_fields: readonly_values}).then(function(r) {
                            self.display_translation_alert(values);
                            return self.record_created(r, prepend_on_create);
                        }, null);
                    } else if (_.isEmpty(values)) {
                        // Not dirty, noop save
                        save_deferral = $.Deferred().resolve({}).promise();
                    } else {
                        // Write save
                        save_deferral = self.dataset.write(self.datarecord.id, values, {readonly_fields: readonly_values}).then(function(r) {
                            self.display_translation_alert(values);
                            if (self.dataset.child_name=='interns_pass_new'){
                                var tmp = self.getParent().getParent().getParent().getParent();
//                                tmp.view_form.reload();
                                tmp.field_manager.fields.interns_cancel_pass.reload_current_view();
                            }
                            return self.record_saved(r);
                        }, null);
                    }
                    save_deferral.then(function(result) {
                        def_process_save.resolve(result);
                    }).fail(function() {
                        def_process_save.reject();
                    });
                }
            });
        } catch (e) {
            console.error(e);
            return def_process_save.reject();
        }
        return def_process_save;
    },

});


return {
    FormViewCustom:FormViewCustom,
    SelectCreateDialogCustom:SelectCreateDialogCustom
};

});