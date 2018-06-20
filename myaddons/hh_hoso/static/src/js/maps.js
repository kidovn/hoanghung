odoo.define('hh.tree_view', function(require) {
"use strict";

var ListView = require('web.ListView');

ListView.include({


//    do_activate_record: function (index, id, dataset, view) {
//        this.dataset.ids = dataset.ids;
//
//        else{
//            this.select_record(index, view);
//        }
//    },
//
    select_record:function (index, view) {
        if(this.dataset.model == 'hh.report' && typeof view == 'undefined'){
            view = 'createreport';
        }
        else{
            view = view || index === null || index === undefined ? 'form' : 'form';
        }
        this.dataset.index = index;
        _.delay(_.bind(function () {
            this.do_switch_view(view);
        }, this));
    },
});
});