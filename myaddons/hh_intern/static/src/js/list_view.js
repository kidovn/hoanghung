odoo.define('hh_intern.ListView', function (require) {
"use strict";

var ControlPanel = require('web.ControlPanel');
var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var common = require('web.form_common');
var ListView = require('web.ListView');

var _t = core._t;
var QWeb = core.qweb;
var FieldMany2Many = core.form_widget_registry.get('many2many');
var FormView = require('web.FormView');

var ListViewNew = ListView.extend({
    _template: 'ListViewNew',
    init: function() {
        var self = this;
        this._super.apply(this, arguments);
        this.header_count_form = 0;
        this.header_count_avatar = 0;
        this.header_count_health = 0;
        this.header_count_deposit = 0;


    },
    set_groups: function (groups) {
        if (this.groups) {
            $(this.groups).unbind("toggle_button_bool toggle_delete_bool toggle_one2many_col");
        }
        this._super(groups);
        var self = this;
        $(this.groups).bind({
            'toggle_button_bool':function(e,id,field,options){
                self.ViewManager.x2m.toggle_button_bool(id,field,options);
            },
            'toggle_delete_bool':function(e,id,field,options){
                self.ViewManager.x2m.toggle_delete_bool(id,field,options);
            },
            'toggle_one2many_col':function(e,id,field,options){
                self.toggle_one2many_col(id,field,options);
            }
        });

    },

    toggle_one2many_col:function(id,field,context){

    },

    do_delete_silent:function(ids)
    {
        var self= this;
        return $.when(this.dataset.unlink(ids)).done(function () {
            _(ids).each(function (id) {
                self.records.remove(self.records.get(id));
            });
            // Hide the table if there is no more record in the dataset
            if (self.display_nocontent_helper()) {
                self.no_result();
            } else {
                if (self.records.length && self.current_min === 1) {
                    // Reload the list view if we delete all the records of the first page
                    self.reload();
                } else if (self.records.length && self.dataset.size() > 0) {
                    // Load previous page if the current one is empty
                    self.pager.previous();
                }
                // Reload the list view if we are not on the last page
                if (self.current_min + self._limit - 1 < self.dataset.size()) {
                    self.reload();
                }
            }
            self.update_pager(self.dataset);
            self.compute_aggregates();
        });

    },

    do_delete: function (ids) {
        var showed = false;
        if (ids.length){
            if(this.dataset.child_name == 'interns_pre'){
                if (this.ViewManager.x2m.getParent().fields.interns_promotion.dataset.ids.indexOf(ids[0]) > -1){
                    showed = true;
                    if(!confirm(_t("TTS này đã được tiến cử, bạn có chắc muốn xoá?"))){
                        return;
                    }
                }
            }
            if (!showed ) {
                if (!(confirm(_t("Do you really want to remove these records?")))){
                    return;
                }
            }
        }
        else{
            return;
        }

        var self = this;

        return $.when(this.dataset.unlink(ids)).done(function () {
            if(self.dataset.child_name == 'interns_pre'){
                if (self.ViewManager.x2m.getParent().fields.interns_promotion.dataset.ids.indexOf(ids[0]) > -1){
                    self.ViewManager.x2m.getParent().fields.interns_promotion.reload_current_view();
                }
            }
            else if(self.dataset.child_name == 'interns_pass'||self.dataset.child_name == 'interns_preparatory'){
                self.ViewManager.x2m.getParent().fields.interns.reload_current_view();
            }
            else if (self.dataset.child_name == 'interns' || self.dataset.child_name == 'interns_escape_exam'){
                 self.ViewManager.x2m.getParent().fields.interns_promotion.reload_current_view();
            }
            _(ids).each(function (id) {
                self.records.remove(self.records.get(id));
            });
            // Hide the table if there is no more record in the dataset
            if (self.display_nocontent_helper()) {
                self.no_result();
            } else {
                if (self.records.length && self.current_min === 1) {
                    // Reload the list view if we delete all the records of the first page
                    self.reload();
                } else if (self.records.length && self.dataset.size() > 0) {
                    // Load previous page if the current one is empty
                    self.pager.previous();
                }
                // Reload the list view if we are not on the last page
                if (self.current_min + self._limit - 1 < self.dataset.size()) {
                    self.reload();
                }
            }
            self.update_pager(self.dataset);
            self.compute_aggregates();
        });
    },
//
    load_list: function() {
//        var self = this;
//
        this.header_count_form = 0;
        this.header_count_iq = 0;
        this.header_count_avatar = 0;
        this.header_count_health = 0;
        this.header_count_deposit = 0;

        for(var i in this.dataset.cache){
//            if(this.dataset.cache[i].values['have_form']){
//                this.header_count_form+=1;
//            }
            if(this.dataset.cache[i].values['have_iq']){
                this.header_count_iq+=1;
            }
            if(this.dataset.cache[i].values['have_health']){
                this.header_count_health+=1;
            }
            if(this.dataset.cache[i].values['have_deposit']){
                this.header_count_deposit+=1;
            }
            if(this.dataset.cache[i].values['avatar']!=false){
                this.header_count_avatar+=1;
            }
        }
//        return this._super();
        var self = this;
        // Render the table and append its content
        this.$el.html(QWeb.render(this._template, _.extend({},this, {
            is_list_pre: function(){
                return self.dataset.child_name === 'interns_pre';
            },
            not_kiemsoat: function(){
                var context = self.dataset.get_context();
                if(context.__contexts && context.__contexts.length>0 && context.__contexts[0].length>0 && context.__contexts[0].includes("'page':'kiemsoat'")){
                    return false;
                }
                return true;
            },
            is_list_exam: function(){
                return self.dataset.child_name == 'interns';
            },
            is_pass_list: function(){
                return self.dataset.child_name == 'interns_pass';
            },
            show_column: function(column){
                if(column.options_tmp  && column.options_tmp.invisible){
                    for(var condition in column.options_tmp.invisible){
                        if ('datarecord' in self.ViewManager.x2m.getParent() && column.options_tmp.invisible[condition].indexOf(self.ViewManager.x2m.getParent().datarecord[condition])>-1){
                            return false;
                        }
                    }
                    return true;

                }
                return true;
            },
            additional_heading_info(column){
                if(column.id == 'have_form'){
                    return '<span style="color:red">('+this.header_count_form+')</span>';
                }
                else if (column.id == 'have_iq'){
                    return '<span style="color:red">('+this.header_count_iq+')</span>';
                }
                else if(column.id == 'have_health'){
                    return '<span style="color:red">('+this.header_count_health+')</span>';
                }else if(column.id == 'have_deposit'){
                    return '<span style="color:red">('+this.header_count_deposit+')</span>';
                }else if(column.id == 'avatar'){
                    return '<span style="color:red">('+this.header_count_avatar+')</span>';
                }
                else return "";
            }
        },)));
        this.$el.addClass(this.fields_view.arch.attrs['class']);
        if (this.grouped) {
            this.$('.o_list_view').addClass('o_list_view_grouped');
        }
        this.$('.o_list_view').append(this.groups.elements);

        // Compute the aggregates and display them in the list's footer
        this.compute_aggregates();

        // Head hook
        // Selecting records
        this.$('thead .o_list_record_selector input').click(function() {
            self.$('tbody .o_list_record_selector input').prop('checked', $(this).prop('checked') || false);
            var selection = self.groups.get_selection();
            $(self.groups).trigger('selected', [selection.ids, selection.records]);
        });

        // Sort
        if (this.dataset._sort.length) {
            if (this.dataset._sort[0].indexOf('-') === -1) {
                this.$('th[data-id=' + this.dataset._sort[0] + ']').addClass("o-sort-down");
            } else {
                this.$('th[data-id=' + this.dataset._sort[0].split('-')[1] + ']').addClass("o-sort-up");
            }
        }

        this.trigger('list_view_loaded', data, this.grouped);

//        this.$('tfoot .o_list_download_excel').click(function() {
//            /
//        });

        return $.when();
    },
});

//var ColumnMany2ManyTags = core.list_widget_registry.get('field').extend({
//    format: function (row_data, options) {
//        return this._super(row_data, options);
//    },
//});
//
//core.list_widget_registry
//    .add('field.many2many_tags', ColumnMany2ManyTags);

return ListViewNew;

});