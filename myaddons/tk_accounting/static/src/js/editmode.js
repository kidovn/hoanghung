odoo.define('tk_accounting.editmode', function (require) {
    "use strict";
    var FormView = require('web.FormView');
    var core = require('web.core');

    var TekoAccountingFormView = FormView.include({
        init: function(parent, dataset, view_id, options) {
            this._super(parent, dataset, view_id, options);
        },
        load_record: function(record) {
            this._super.apply(this, arguments);
            if (this.model ==='tk.accounting.three.pl.paid.detail') {
                if (!['draft', 'invalid', 'need_check', 'not_found'].includes(record.state)) {
                    this.$buttons.find('.o_form_button_edit').first().remove();
                    this.$buttons.find('.o_form_button_create').first().remove();
                }
            }
        }

    });

    // core.view_registry.add('form', TekoFormView);

    return TekoAccountingFormView;
});