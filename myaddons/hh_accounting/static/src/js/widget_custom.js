odoo.define('hh_accounting.WidgetCustom', function (require) {
    "use strict";
    var core = require('web.core');
    var session = require('web.session');
    var common = require('web.form_common');
    var QWeb = core.qweb;
    var list_widget_registry = core.list_widget_registry;
    var _t = core._t;
    var pyeval = require('web.pyeval');
    var Dialog = require('web.Dialog');



    var Column = list_widget_registry.get('field');


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

    var FieldBooleanButton = common.AbstractField.extend(common.ReinitializeFieldMixin,{
        className: 'o_stat_info',
        events: {
            'click button': 'on_click',
        },
        init: function() {
            this._super.apply(this, arguments);
            switch (this.options["terminology"]) {
                case "active":
                    this.string_true = _t("Active");
                    this.action_true = _t("Deactivate");
                    this.string_false = _t("Inactive");
                    this.action_false = _t("Activate");
                    break;
                case "archive":
                    this.string_true = _t("Active");
                    this.action_true = _t("Archive");
                    this.string_false = _t("Archived");
                    this.action_false = _t("Unarchive");
                    break;
                default:
                    var terms = typeof this.options["terminology"] === 'string' ? {} : this.options["terminology"];
                    this.string_true = _t(terms.string_true || "On");
                    this.action_true = _t(terms.action_true || terms.string_false || "Switch Off");
                    this.string_false = _t(terms.string_false || "Off");
                    this.action_false = _t(terms.action_false || terms.string_true || "Switch On");
            }
        },

        render_value: function() {
            this._super();
            this.$el.html(QWeb.render("MyAccountingButton", {widget: this}));
        },
        is_false: function() {
            return false;
        },

        on_click: function(event) {
            event.preventDefault();

            var self = this;
            Dialog.confirm(this, "Bạn có chắc chắn về hành động này?", {
                confirm_callback: function() {
//                    self.ds_contacts.call('unlink_from_partner_id', [id]).then(function () {
//                        self._remove_filter(id);
//                        self.reload();
//                    });
                    var value = self.get('value');
                    self.internal_set_value(!self.get('value'));
                    self.render_value();
//                    self.set_value(self.get('value'));

                },
            });
//            this.trigger("dialog_opened", dialog);
//            return dialog;
        },
    });

    list_widget_registry.add('field.accounting_button', ColumnBoolButton);
    core.form_widget_registry.add('accounting_button', FieldBooleanButton);

});