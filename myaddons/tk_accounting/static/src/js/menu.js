odoo.define('tk_accounting.Menu', function (require) {
    "use strict";

    var Menu = require('web.Menu');

    var tekoAccountingMqMenuWidget = Menu.include({
        on_menu_click: function(ev) {
            ev.preventDefault();
            var self = this;
            var _menu_counter_id = 'div#menu_counter';
            var _menu_counter = $(ev.currentTarget).find(_menu_counter_id);
            if (_menu_counter.length <= 0) {
                _menu_counter = $(ev.target);
            }
            var _needaction = _menu_counter.is(_menu_counter_id);
            var _menu_id = $(ev.currentTarget).data('menu');
            if (_needaction) {
                self.do_load_needaction([_menu_id]).then(function () {
                    self.trigger("need_action_reloaded");
                });
            }
            self.menu_click(_menu_id, _needaction);
        }
    });
});