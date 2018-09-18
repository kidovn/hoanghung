odoo.define('tk_accounting.listview', function (require) {
    "use strict";
    
    var ListView = require('web.ListView');
    var Model = require('web.DataModel');

    var testWidget = ListView.include({
        render_buttons: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.on('click', '.oe_map_price_button', function () {
                    console.log("button click : " + this.id);
                    var selected = [];
                    $('.o_checkbox input:checked').each(function () {
                        var id = $(this).parent().parent().parent().attr("data-id");
                        if ( id != null ){
                            selected.push(id);
                        }
                    });
                    if( selected.length >0){
                        var model_name = this.id;
                        var model = new Model(model_name);
                        model.call("map",[selected]).then(function(action){
                            if (action != null){
                                // self.do_action accepts the action parameter and opens the new view
                                self.do_action(action);
                            }
                            else{
                                console.log("Cannot send action");
                            }
                        });
                    } else {
                        alert('Please select item to process');
                    }
                });
                this.$buttons.on('click', '.oe_update_button', function () {
                    console.log("button click : " + this.id);
                    var selected = [];
                    $('.o_checkbox input:checked').each(function () {
                        var id = $(this).parent().parent().parent().attr("data-id");
                        if ( id != null ){
                            selected.push(id);
                        }
                    });
                    if( selected.length >0){
                        var model_name = this.id;
                        var model = new Model(model_name);
                        model.call("update",[selected]).then(function(action){
                            if (action != null){
                                // self.do_action accepts the action parameter and opens the new view
                                self.do_action(action);
                            }
                            else{
                                console.log("Cannot send action");
                            }
                        });
                    } else {
                        alert('Please select item to process');
                    }
                });
                this.$buttons.on('click', '.oe_validate_three_pl_paid_button', function () {
                    console.log("button click : " + this.id);
                    var selected = [];
                    $('.o_checkbox input:checked').each(function () {
                        var id = $(this).parent().parent().parent().attr("data-id");
                        if ( id != null ){
                            selected.push(id);
                        }
                    });
                    if( selected.length >0){
                        var model_name = this.id;
                        var model = new Model(model_name);
                        model.call("validate_three_pl_paid",[selected]).then(function(action){
                            var _datagroup = self.groups.datagroup;
                            self.do_search(_datagroup.domain, _datagroup.context, _datagroup.group_by).then(function(){
                                var _menu = self.ViewManager.action_manager.webclient.menu;
                                var _list_menu_counters = 'div.badge';
                                var _menu_counters = $.find(_list_menu_counters);
                                if (_menu_counters.length <= 0) {
                                    _menu_counters = $(ev.target);
                                }
                                var tmp_self = self;
                                $.each(_menu_counters, function (index, _menu_counter) {
                                    if (_menu_counter && _menu_counter.parentElement) {
                                        var _menu_id = _menu_counter.parentElement.getAttribute('data-menu');
                                        if (_menu_id) {
                                            _menu.do_load_needaction([parseInt(_menu_id)]).then(function () {
                                                tmp_self.trigger("need_action_reloaded");
                                            });
                                        }
                                    }
                                })
                            })
                        });
                    } else {
                        alert('Please select item to process');
                    }
                });

                this.$buttons.on('click', '.oe_validate_three_pl_confirm_paid_button', function () {
                   console.log("button click : " + this.id);
                    var selected = [];
                    $('.o_checkbox input:checked').each(function () {
                        var id = $(this).parent().parent().parent().attr("data-id");
                        if ( id != null ){
                            selected.push(id);
                        }
                    });
                    if( selected.length >0){
                        var model_name = this.dataset.model;
                        var model = new Model(model_name);
                        model.call("confirm_three_pl_paid",[selected]).then(function(action){
                            var _datagroup = self.groups.datagroup;
                            self.do_search(_datagroup.domain, _datagroup.context, _datagroup.group_by).then(function(){
                                var _menu = self.ViewManager.action_manager.webclient.menu;
                                var _list_menu_counters = 'div.badge';
                                var _menu_counters = $.find(_list_menu_counters);
                                if (_menu_counters.length <= 0) {
                                    _menu_counters = $(ev.target);
                                }
                                var tmp_self = self;
                                $.each(_menu_counters, function (index, _menu_counter) {
                                    if (_menu_counter && _menu_counter.parentElement) {
                                        var _menu_id = _menu_counter.parentElement.getAttribute('data-menu');
                                        if (_menu_id) {
                                            _menu.do_load_needaction([parseInt(_menu_id)]).then(function () {
                                                tmp_self.trigger("need_action_reloaded");
                                            });
                                        }
                                    }
                                })
                            })
                        });
                    } else {
                        alert('Please select item to process');
                    }
                });

                this.$buttons.on('click', '.oe_validate_three_pl_revalidate_paid_button', function () {
                   console.log("button click : " + this.id);
                    var selected = [];
                    $('.o_checkbox input:checked').each(function () {
                        var id = $(this).parent().parent().parent().attr("data-id");
                        if ( id != null ){
                            selected.push(id);
                        }
                    });
                    if( selected.length >0){
                        var model_name = this.dataset.model;
                        var model = new Model(model_name);
                        model.call("revalidate_three_pl_paid",[selected]).then(function(action){
                            var _datagroup = self.groups.datagroup;
                            self.do_search(_datagroup.domain, _datagroup.context, _datagroup.group_by).then(function(){
                                var _menu = self.ViewManager.action_manager.webclient.menu;
                                var _list_menu_counters = 'div.badge';
                                var _menu_counters = $.find(_list_menu_counters);
                                if (_menu_counters.length <= 0) {
                                    _menu_counters = $(ev.target);
                                }
                                var tmp_self = self;
                                $.each(_menu_counters, function (index, _menu_counter) {
                                    if (_menu_counter && _menu_counter.parentElement) {
                                        var _menu_id = _menu_counter.parentElement.getAttribute('data-menu');
                                        if (_menu_id) {
                                            _menu.do_load_needaction([parseInt(_menu_id)]).then(function () {
                                                tmp_self.trigger("need_action_reloaded");
                                            });
                                        }
                                    }
                                })
                            })
                        });
                    } else {
                        alert('Please select item to process');
                    }
                });

                if (this.model == "tk.accounting.three.pl.paid.detail") {
                    if (/duplicated/.test(self.ViewManager.action.xml_id)
                        || /_valid/.test(self.ViewManager.action.xml_id)
                        || /invalid/.test(self.ViewManager.action.xml_id)
                        || /error/.test(self.ViewManager.action.xml_id)
                        || /completed/.test(self.ViewManager.action.xml_id)) {
                        self.$buttons.find('.oe_validate_three_pl_paid_button').first().remove();
                    }
                    if (/draft/.test(self.ViewManager.action.xml_id)
                        || /invalid/.test(self.ViewManager.action.xml_id)
                        || /duplicated/.test(self.ViewManager.action.xml_id)
                        || /error/.test(self.ViewManager.action.xml_id)
                        || /completed/.test(self.ViewManager.action.xml_id)) {
                        self.$buttons.find('.oe_validate_three_pl_confirm_paid_button').first().remove();
                    }
                    if (/valid/.test(self.ViewManager.action.xml_id)
                        || /invalid/.test(self.ViewManager.action.xml_id)
                        || /duplicated/.test(self.ViewManager.action.xml_id)
                        || /error/.test(self.ViewManager.action.xml_id)
                        || /completed/.test(self.ViewManager.action.xml_id)) {
                        self.$buttons.find('.o_button_import').first().remove();
                    }
                    if (/draft/.test(self.ViewManager.action.xml_id)
                        || /_valid/.test(self.ViewManager.action.xml_id)
                        || /invalid/.test(self.ViewManager.action.xml_id)
                        || /duplicated/.test(self.ViewManager.action.xml_id)
                        || /error/.test(self.ViewManager.action.xml_id)
                        || /completed/.test(self.ViewManager.action.xml_id)) {
                        self.$buttons.find('.o_list_button_add').first().remove();
                    }
                    if (/draft/.test(self.ViewManager.action.xml_id)
                        || /_valid/.test(self.ViewManager.action.xml_id)
                        || /duplicated/.test(self.ViewManager.action.xml_id)
                        || /error/.test(self.ViewManager.action.xml_id)
                        || /completed/.test(self.ViewManager.action.xml_id)) {
                        self.$buttons.find('.oe_validate_three_pl_revalidate_paid_button').first().remove();
                    }

                    var tmp_this = this;
                    var tmp_view_manager = self.ViewManager;
                    this.$('.o_checkbox').click(function () {
                        if (!/draft/.test(tmp_view_manager.action.xml_id)) {
                            if (tmp_this.sidebar.$el.find('.o_cp_sidebar').first()
                                && tmp_this.sidebar.$el.find('.o_cp_sidebar').first().context
                                && tmp_this.sidebar.$el.find('.o_cp_sidebar').first().context.style) {
                                tmp_this.sidebar.$el.find('.o_cp_sidebar').first().context.style.display = "none";
                            }
                        }
                    })
                }
            }
        }
    });
});