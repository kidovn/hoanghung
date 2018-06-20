odoo.define('hh_hoso.FavoriteMenu', function (require) {
"use strict";

var core = require('web.core');
var data_manager = require('web.data_manager');
var pyeval = require('web.pyeval');
var myeval = require('hh.pyeval');
var session = require('web.session');
var Widget = require('web.Widget');
var py = window.py;

var _t = core._t;

var FavoriteMenu = require('web.FavoriteMenu');

FavoriteMenu.include({
    save_favorite: function () {
        var self = this,
            filter_name = this.$inputs[0].value,
            default_filter = this.$inputs[1].checked,
            shared_filter = this.$inputs[2].checked;
        if (!filter_name.length){
            this.do_warn(_t("Error"), _t("Filter name is required."));
            this.$inputs.first().focus();
            return;
        }
        if (_.chain(this.filters)
                .pluck('name')
                .contains(filter_name).value()) {
            this.do_warn(_t("Error"), _t("Filter with same name already exists."));
            this.$inputs.first().focus();
            return;
        }
        var search = this.searchview.build_search_data(),
            view_manager = this.findAncestor(function (a) {
                // HORRIBLE HACK. PLEASE SAVE ME FROM MYSELF (BUT IN A PAINLESS WAY IF POSSIBLE)
                return 'active_view' in a;
            }),
            view_context = view_manager ? view_manager.active_view.controller.get_context() : {},

            results = myeval.sync_eval_domains_and_contexts({
                domains: search.domains,
                contexts: search.contexts.concat(view_context || []),
                group_by_seq: search.groupbys || [],
            });

//            results = {
//                domain: search.domains,
//                context: search.contexts.concat(view_context || []),
//                group_by_seq: search.groupbys || [],
//            };
        if (!_.isEmpty(results.group_by)) {
            results.context.group_by = results.group_by;
        }
        // Don't save user_context keys in the custom filter, otherwise end
        // up with e.g. wrong uid or lang stored *and used in subsequent
        // reqs*
//        var ctx = results.context;
//        _(_.keys(session.user_context)).each(function (key) {
//            delete ctx[key];
//        });
        var domain = JSON.stringify(results.domain);
        while(domain.indexOf('"time.')>-1){
            domain = domain.replace('"time.','time.').replace('(\\"','("').replace('\\")"','")');
        }
        var filter = {
            name: filter_name,
            user_id: shared_filter ? false : session.uid,
            model_id: this.target_model,
            context: results.context,
            domain: domain,
            sort: JSON.stringify(this.searchview.dataset._sort),
            is_default: default_filter,
            action_id: this.action_id,
        };
        return data_manager.create_filter(filter).done(function (id) {
            filter.id = id;
            self.toggle_save_menu(false);
            self.$save_name.find('input').val('').prop('checked', false);
            self.add_filter(filter);
            self.append_filter(filter);
            self.toggle_filter(filter, true);
        });
    },
//    self_eval_domain:function(domains){
//
//        var result = [];
//         _.each(domains, function (domain) {
//            if (_.isString(domain)){
//                result.push(JSON.parse(domain));
//            }
//            else{
//                result.push(domain);
//            }
//         });
//         return result;
//    },


});


});