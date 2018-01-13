odoo.define('intern.invoice', function (require) {
    "use strict";

    var ListView = require('web.ListView');
    var Model = require('web.DataModel');

    var testWidget = ListView.include({
        sort_by_column: function (e) {
            e.stopPropagation();
            var $column = $(e.currentTarget);
            var col_name = $column.data('id');
            var field = this.fields_view.fields[col_name];
            // test whether the field is sortable
            if (field && !field.sortable) {
                return false;
            }
            this.dataset.sort(col_name);
            if($column.hasClass("o-sort-down") || $column.hasClass("o-sort-up"))  {
                $column.toggleClass("o-sort-up o-sort-down");
            } else {
                $column.addClass("o-sort-down");
            }
            $column.siblings('.o_column_sortable').removeClass("o-sort-up o-sort-down");

//            var field_values = this.get_fields_values();

            $.urlParam = function(name){
                var results = new RegExp('[#\?&]' + name + '=([^&#]*)').exec(window.location.href);
                if (results==null){
                   return null;
                }
                else{
                   return results[1] || 0;
                }
            }
//            console.error(window.location.href);
//            console.error(col_name +" "  + $.urlParam('id'));
//            var active_id = this.getParent().getParent().dataset.ids[this.dataset.index];
            var model = new Model("intern.invoice");
            var state = 0;
            if($column.hasClass("o-sort-down")){
                state = 0;
            }
            else{
                state = 1;
            }

            model.call("on_order_changed",[$.urlParam('id'),col_name,state]).then(function(result) {

            });

            return this.reload_content();
        }

    });
});