/*
 * © 2016 Camptocamp SA
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
 */
odoo.define('web_access_rule_buttons.main', function (require) {
  "use strict";

  var core = require('web.core');

  var FormView = require('web.FormView');

  FormView.include({
    load_record: function() {
      var self = this;
      return this._super.apply(this, arguments)
        .then(function() {
          self.hide_edit_button();
        });
    },

    hide_edit_button: function() {
      if (this.model == 'tk.accounting.reduce.debt' && this.datarecord.state == 'approved') {
          this.$buttons.find('.o_form_button_edit').addClass('o_disabled').prop('disabled', true);
      }
      if (this.model == 'tk.accounting.change.debt' && this.datarecord.state == 'approved') {
          this.$buttons.find('.o_form_button_edit').addClass('o_disabled').prop('disabled', true);
      }
    }

  });

});
