odoo.define('hh_hoso.FieldWidget', function (require) {
"use strict";

var common = require('web.list_common');

var core = require('web.core');
var session = require('web.session');
var QWeb = core.qweb;
var list_widget_registry = core.list_widget_registry;
var common = require('web.form_common');

var FieldButtonBoolean = common.AbstractField.extend({
    template: "FieldButtonWidget",
    events: {
        'click': 'set_toggle_button'
    },
    render_value: function () {
        var class_name = this.get_value() ? 'o_toggle_button_success' : 'text-muted';
        this.$('i').attr('class', ('fa fa-circle ' + class_name));
    },
    set_toggle_button: function () {
        var self = this;
        var toggle_value = !this.get_value();
        if (this.view.get('actual_mode') == 'view') {
            var rec_values = {};
            rec_values[self.node.attrs.name] = toggle_value;
            return this.view.dataset._model.call(
                    'write', [
                        [this.view.datarecord.id],
                        rec_values,
                        self.view.dataset.get_context()
                    ]).done(function () { self.reload_record(); });
        }
        else {
            this.set_value(toggle_value);
        }
    },
    reload_record: function () {
        this.view.reload();
    },
    is_false: function() {
        return false;
    },
});

list_widget_registry.add('field.boolbutton', FieldButtonBoolean);

});