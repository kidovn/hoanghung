
odoo.define('hh_hoso.ReportCreation', function (require) {
"use strict";


var ControlPanelMixin = require('web.ControlPanelMixin');
var Widget = require('web.Widget');
var session = require('web.session');
var core = require('web.core');
var data = require('web.data');
var data_manager = require('web.data_manager');
var datepicker = require('web.datepicker');
var FilterMenu = require('hh_hoso.FilterMenu');
var DynamicListView = require('hh_hoso.DynamicListView');
var Model = require('web.Model');
var QWeb = core.qweb;
var session = require('web.session');
var pyeval = require('web.pyeval');
var ajax = require('web.ajax');
var crash_manager = require('web.crash_manager');
var framework = require('web.framework');
var _t = core._t;
var View = require('web.View');
var utils = require('web.utils');

var DataManager = require('web.DataManager');

DataManager.include({

    load_fields_for_report: function (dataset) {
        if(!this._cache.fields_report){
            this._cache['fields_report'] = {};
        }
        if (!this._cache.fields_report[dataset.model]) {
            this._cache.fields_report[dataset.model] = dataset.call('fields_get_for_report', {
                context: dataset.get_context(),
            }).fail(this._invalidate.bind(this, this._cache.fields_report, dataset.model));
        }
        return this._cache.fields_report[dataset.model];
    },

});

var CreateReport = View.extend({
    template: 'hh_hoso.create_report_view',

    multi_record: false,
    // Indicates that this view is not searchable, and thus that no search view should be displayed.
    searchable: false,

    defaults: _.extend({}, View.prototype.defaults, {
        not_interactible_on_create: false,
        initial_mode: "view",
        disable_autofocus: false,
        footer_to_buttons: false,
    }),

    events: {
        "click .o_report_field": function (event) {
            event.preventDefault();
            if(this.get("actual_mode") !== "view"){
                var channel_id = this.$(event.currentTarget).data('field-id');
                var model = this.$(event.currentTarget).closest('div').data('model');
                this.set_field(channel_id,model);
            }
        },
        "click button.o_lookup": function(event){
            this.start_search();
        },
//        "focus .input_date_start": function(event){
//            var self = this;
//
//            return this.datewidget.$input.focus();
//        }
//        "click button.o_save_report": function(event){
//            this.save_report();
//        },
//        "click button.o_form_button_create":function(event){
//            this.on_button_create();
//        },
//         "click button.o_form_button_edit":function(event){
//            this.on_button_edit();
//        },
//        "click button.o_form_button_save":function(event){
//            this.on_button_save();
//        },
//        "click button.o_form_button_cancel":function(event){
//            this.on_button_cancel();
//        },

         "click button.export_report":function(event){
            this.on_button_export_report();
        },
    },

    _render_breadcrumbs_li: function (bc, index, length) {
        var self = this;
        var is_last = (index === length-1);
        var li_content = bc && _.escape(bc.trim()) || data.noDisplayContent;
        var $bc = $('<li>')
            .append(is_last ? li_content : $('<a>').html(li_content))
            .toggleClass('active', is_last);
//        if (!is_last) {
//            $bc.click(function () {
//                self.trigger("on_breadcrumb_click", bc.action, bc.index);
//            });
//        }
        return $bc;
    },

//    setupFocus: function ($e) {
//        var self = this;
//        $e.on({
//            focus: function () { self.trigger('focused'); },
//            blur: function () { self.trigger('blurred'); }
//        });
//    },

    init: function() {
        this._super.apply(this, arguments);
        this.action_manager = this.ViewManager.action_manager;
        this.fields = {};
        var self =this;
        this.datarecord = {};
//        if(typeof this.action.res_id !== 'undefined'){
//            this.datarecord.id = this.action.res_id;
//        }
//        this.fields = [
//            {'stt':0,'name':'name','string':'Tên','type':'char'},
//            {'stt':1,'name':'blood_group','string':'Nhóm máu','type':'selection'}];


        this.dataset_report = new data.DataSetSearch(this, 'hh.report');
//        this.dataset_invoice = new data.DataSetSearch(this, 'intern.invoice');

        this.selected_fields = {};
        this.selected_fields['intern.intern'] = [];
        this.selected_fields['intern.internclone'] = [];
        this.datewidget_start = new datepicker.DateWidget(this);
        this.datewidget_start.appendTo('<div>').done(function() {
//            self.datewidget.$el.addClass(self.$el.attr('class'));
//            self.$('date_picker').replaceElement(self.datewidget.$el);
//            self.datewidget.$input.addClass('o_form_input');
//            self.setupFocus(self.datewidget.$input);
        });


        this.datewidget_end = new datepicker.DateWidget(this);
        this.datewidget_end.appendTo('<div>');

        this.dynamicListView;

        this.has_been_loaded = $.Deferred();
        this.is_initialized = $.Deferred();

        this.set({actual_mode: this.options.initial_mode});
        this.has_been_loaded.done(function() {
            self.on("change:actual_mode", self, self.toggle_buttons);
            self.on("change:actual_mode", self, self.toggle_sidebar);
        });
        self.on("load_record", self, self.load_record);

    },


    toggle_sidebar: function() {
        if (this.sidebar) {
            this.sidebar.do_toggle(this.get("actual_mode") === "view");
        }
    },


    is_action_enabled: function(action) {
        return true;
    },

    toggle_buttons: function() {
        var view_mode = this.get("actual_mode") === "view";
        if (this.$buttons) {
            this.$buttons.find('.o_form_buttons_view').toggle(view_mode);
            this.$buttons.find('.o_form_buttons_edit').toggle(!view_mode);
        }
    },

    render_buttons: function($node) {
//        this.$buttons = $('<div/>');
//
//        var $footer = this.$('footer');
//        this.$buttons.append(QWeb.render("FormView.buttons", {'widget': this}));
//        if (this.options.footer_to_buttons) {
//            $footer.appendTo(this.$buttons);
//        }
//
//        // Show or hide the buttons according to the view mode
//        this.toggle_buttons();
////        this.$buttons.on('click', '.o_form_button_create', this.on_button_create);
////        this.$buttons.on('click', '.o_form_button_edit', this.on_button_edit);
////        this.$buttons.on('click', '.o_form_button_save', this.on_button_save);
////        this.$buttons.on('click', '.o_form_button_cancel', this.on_button_cancel);
//
//        this.$buttons.appendTo($node);

        this.$buttons = $('<div/>');

        var $footer = this.$('footer');
        if (this.options.action_buttons !== false || this.options.footer_to_buttons && $footer.children().length === 0) {
            this.$buttons.append(QWeb.render("FormView.buttons", {'widget': this}));
        }
        if (this.options.footer_to_buttons) {
            $footer.appendTo(this.$buttons);
        }

        // Show or hide the buttons according to the view mode
        this.toggle_buttons();
        this.$buttons.on('click', '.o_form_button_create', this.on_button_create);
        this.$buttons.on('click', '.o_form_button_edit', this.on_button_edit);
        this.$buttons.on('click', '.o_form_button_save', this.on_button_save);
        this.$buttons.on('click', '.o_form_button_cancel', this.on_button_cancel);

        this.$buttons.appendTo($node);
    },

    get_fields: function () {
        if (!this._fields_def) {
            this._fields_def = data_manager.load_fields_for_report(this.dataset_report).then(function (data) {
//                var fields = {
//                    id: { string: 'ID', type: 'id', searchable: true }
//                };
//                _.each(fields, function(field_def, field_name) {
////                    if (field_def.selectable !== false && field_name !== 'id') {
//                        fields[field_name] = field_def;
////                    }
//                });
                return data;
            });
        }
        return this._fields_def;
    },

    clear_selected_field: function(){
        for(var key in this.selected_fields){
            for(var i = 0; i<this.selected_fields[key].length;i++){
                var field= this.selected_fields[key][i];
                this.$(".o_fields_head").find("[field-id='"+field['filter'].data_field.name+"']").detach();
                this.refresh_sidebar(field['id'],key,false);
            }
        }
        this.selected_fields = {};
        this.selected_fields['intern'] = [];
        this.selected_fields['internclone'] = [];
        this.selected_fields['invoice'] = [];

    },

    set_field: function (index,model) {
        var self = this;
        var data_field = this.fields[model][parseInt(index)]
        var selected_index =  this.selected_fields[model].findIndex(x => x.id==index);
        if (selected_index > -1) {
            this.selected_fields[model].splice(selected_index, 1);
            self.$(".o_fields_head").find("[field-id='"+data_field.name+"']").detach();
            this.refresh_sidebar(index,model,false);
        }
        else{
            var filterMenu = new FilterMenu(this,data_field);

            filterMenu.appendTo(self.$(".o_fields_head"));

            this.selected_fields[model].push({'id':index,'filter':filterMenu});
            this.refresh_sidebar(index,model,true);

        }

    },

    refresh_sidebar: function(index,model,add){
       var model = this.$(".o_report_creator_sidebar").find("[data-model='"+model+"']");
       if (add){
            $(model[0]).find("[data-field-id='"+index+"']").addClass('button_selected');
       }else{
            $(model[0]).find("[data-field-id='"+index+"']").removeClass('button_selected');
       }

    },

    load_defaults: function () {
        var self = this;
        self.clear_selected_field();
        var keys = _.keys(this.fields_view.fields);
        if (keys.length) {
            return this.dataset.default_get(keys).then(function(r) {
                self.trigger('load_record', _.clone(r));
            });
        }
        return $.when().then(this.trigger.bind(this, 'load_record', {}));
    },

    can_be_discarded: function(message) {
        return $.Deferred().resolve();
    },

    on_button_new: function() {
        return $.when(this.has_been_loaded)
            .then(this.can_be_discarded.bind(this))
            .then(this.load_defaults.bind(this));
    },

    to_edit_mode: function() {
        this.$('#report_name')[0].readOnly = false;
        this.onchanges_mutex = new utils.Mutex();
        this._actualize_mode("edit");
        this.trigger('to_edit_mode');
    },

    on_button_edit: function(){
        return this.to_edit_mode();
    },
    on_button_create: function(){
//        this._actualize_mode('create');
//         this.toggle_buttons();
        this.dataset.index = null;
        this.clear_selected_field();
        this.do_show();
    },
    on_button_cancel: function() {
        var self = this;
        this.can_be_discarded().then(function() {
            if (self.get('actual_mode') === 'create') {
                self.trigger('history_back');
            } else {
                self.clear_selected_field();
                self.to_view_mode();
                $.when.apply(null, self.render_value_defs).then(function(){
                    self.trigger('load_record', self.datarecord);
                });
            }
        });
        this.trigger('on_button_cancel');
        return false;
    },

    to_view_mode: function() {
        this.$('#report_name')[0].readOnly = true;
        this._actualize_mode("view");
        this.trigger('to_view_mode');
    },

    on_button_save: function(){
        var self = this;
        return this.save_report().then(function(result) {
            self.trigger("save", result);
            return self.reload().then(function() {
                self.to_view_mode();
                core.bus.trigger('do_reload_needaction');
                core.bus.trigger('form_view_saved', self);
            }).always(function() {
                self.enable_button();
            });
        }).fail(function(){
            self.enable_button();
        });
    },

    enable_button: function () {
        this.$('.oe_form_buttons,.o_statusbar_buttons').add(this.$buttons).find('button.o_disabled').removeClass('o_disabled').prop('disabled', false);
        this.is_disabled = false;
    },

    _actualize_mode: function(switch_to) {
        var mode = switch_to || this.get("actual_mode");
        if (! this.datarecord.id) {
            mode = "create";
        } else if (mode === "create") {
            mode = "edit";
        }

        var viewMode = (mode === "view");
        this.$el.toggleClass('o_form_readonly', viewMode).toggleClass('o_form_editable', !viewMode);

//        this.render_value_defs = [];
        this.set({actual_mode: mode});

//        if(!viewMode) {
//            this.autofocus();
//        }
    },

    save_report: function(){

        var def_process_save = $.Deferred();
        var test = this.$("#report_name");
        var report_name=test[0].value;

        if(!report_name || 0 === report_name.trim().length){
            this.$(".o_report_name").toggleClass("o_form_invalid",true);

            var warnings =  '<ul><li>Tên báo cáo</li></ul>'
            this.do_warn(_t("The following fields are invalid:"), warnings);

            return def_process_save.reject();
        }
        else{
            this.$(".o_report_name").toggleClass("o_form_invalid",false);
        }

        var search = this.build_search_data();
        var fields = [];
        var self = this;
        for (var key in this.selected_fields){
            for (var i = 0; i< this.selected_fields[key].length;i++){
                fields.push(this.selected_fields[key][i]['filter'].data_field['name']);
            }
        }

        var args = {domain:JSON.stringify(search.domains),model:'intern.intern',name:report_name,field_view:JSON.stringify(fields)};

        if(this.datarecord.id){

             var P = new Model('hh.report').call('write',[[this.datarecord.id],args],{context: session.user_context}).then(function(r){
                self._actualize_mode('view');

                def_process_save.resolve(r);
            },null).fail(function(err, event){
                def_process_save.reject();
            });
            return P;
        }
        else{
            var P = new Model('hh.report').call('create',[args],{context: session.user_context}).then(function(r){
                self.datarecord.id = r;
                self.action_manager.do_push_state({
                    id: self.datarecord.id,
                });
                self._actualize_mode('view');

                def_process_save.resolve(r);

            },null).fail(function(err, event){
                def_process_save.reject();
            });

             return P;

        }


    },

    start_search: function(){

        var date_option = {}

        date_option['start'] = datewidget_start.get_value();
        date_option['end'] = datewidget_end.get_value();
        date_option['option'] = this.$('#options_date').val();

        var search = this.build_search_data();
        var domain = {};
        for(var key in search){
            domain[key]= (search[key].domains);
        }

        var fields = [];
        var columns = [];
        for(var key in this.selected_fields){
            for (var i = 0; i< this.selected_fields[key].length;i++){
                fields.push(this.selected_fields[key][i]['filter'].data_field['name']);
                columns.push(this.selected_fields[key][i]['filter'].data_field);
            }
        }

        if(search['intern.internclone']){
            this.search('intern.internclone',domain, search.contexts, search.groupbys,fields,columns,date_option);
        }
        else{
            this.search('intern.intern',domain, search.contexts, search.groupbys,fields,columns,date_option);
        }

    },

    search: function(model,domains, contexts, groupbys,fields,columns,date_option) {
        var self = this;

        if ((typeof this.dynamicListView) !== "undefined"){
            this.dynamicListView.destroy();
        }

        this.dynamicListView = new DynamicListView(this,model,domains,contexts,fields,columns,date_option);

        this.dynamicListView.render_pager();
        if ((typeof this.dynamicListView.pager) !== "undefined"){
//            this.dynamicListView.pager.$el.addClass('o_x2m_control_panel');
            var $header = $('<div/>').addClass('my_cp_pager');
            this.dynamicListView.pager.appendTo($header);
//            this.dynamicListView.pager.appendTo(self.$('.mypager'))
            $header.appendTo(self.$('.mypager'));

        }

        this.dynamicListView.appendTo(self.$(".main_content"));

    },

    on_button_export_report: function(){
        var search = this.build_search_data();
        var fields = [];
        for (var i = 0; i< this.selected_fields.length;i++){
            fields.push({'name':this.selected_fields[i]['filter'].data_field['name'],
                          'string': this.selected_fields[i]['filter'].data_field['string']});
        }

        var form_values = {
            model: 'intern.intern',
            fields: fields,
            domain: pyeval.eval('domains',
                    [search.domains]),
//            offset:0,
            filename:'AAA.csv'
        }

        framework.blockUI();
        this.session.get_file({
            url: '/web/dataset/make_report',
            data: {data: JSON.stringify({
                model: 'intern.intern',
                fields: fields,
                domain: pyeval.eval('domains',
                    [search.domains]),
                context:{"lang":"en_US","tz":"Asia/Ho_Chi_Minh","uid":1,"params":{"action":174}}
            })},
            complete: framework.unblockUI,
            error: crash_manager.rpc_error.bind(crash_manager),
        });

    },

    build_search_data: function(){
        var search_data = {};
        for(var key in this.selected_fields){
            var domains = [], contexts = [], groupbys = [];
            for ( var i =0; i< this.selected_fields[key].length; i++){
                var selected_field = this.selected_fields[key][i];
                for (var j = 0; j< selected_field['filter'].filters_group.length;j++){
                    for (var k =0; k<selected_field['filter'].filters_group[j].filters.length;k++){
                        var field = selected_field['filter'].filters_group[j].filters[k];
                        var domain = field.attrs.domain;
                        if (domain) {

                            domains = domains.concat(domain);
                        }
                    }
                }
            }
            search_data[key] = {
                domains: domains,
                contexts: contexts,
                groupbys: groupbys,
            };
        }
        return search_data;
    },

    update_pager: function() {
        if (this.pager) {
            // Hide the pager in create mode
            if (this.get("actual_mode") === "create") {
                this.pager.do_hide();
            } else {
                this.pager.update_state({size: this.dataset.ids.length, current_min: this.dataset.index + 1});
            }
        }
    },



    load_record: function(record) {
        var self = this, set_values = [];
        if (!record) {
            this.set({ 'title' : undefined });
            this.do_warn(_t("Form"), _t("The record could not be found in the database."), true);
            return $.Deferred().reject();
        }
        this.datarecord = record;

        if(this.datarecord.field_view){
            self.datarecord.field_view_tmp = JSON.parse(self.datarecord.field_view);
        }
        if(this.datarecord.domain){
            self.datarecord.domain_tmp = JSON.parse(self.datarecord.domain);
        }

        if(this.datarecord.field_view_tmp){
            for (var i =0; i<this.datarecord.field_view_tmp.length;i++){
                var exist = false;
                for(var j = 0; j<this.fields['intern.intern'].length;j++){
                    if(this.fields['intern.intern'][j].name == this.datarecord.field_view_tmp[i]){
                        this.set_field(j,'intern.intern');
                        exist = true;
                        break;
                    }
                }
                if(!exist){
                    for(var j = 0; j<this.fields['intern.internclone'].length;j++){
                        if(this.fields['intern.internclone'][j].name == this.datarecord.field_view_tmp[i]){
                            this.set_field(j,'intern.internclone');

                            break;
                        }
                    }
                }
            }
        }
        if(this.datarecord.domain_tmp){
            for(var i = 0; i<this.datarecord.domain_tmp.length;i++){
                var selected_index =  this.selected_fields.findIndex(x => x.filter.data_field.name==this.datarecord.domain_tmp[i][0]);
                if (selected_index > -1) {
                    this.selected_fields[selected_index]['filter'].add_filter(this.datarecord.domain_tmp[i]);
                }
            }
        }

        if(!record.id){
//            for(var i = 0; i<this.fields['intern'].length;i++){
//                if(this.fields['intern'][i].name == 'name'){
//                    this.set_field(i,'intern');
//                    break;
//                }
//            }
//            for(var i = 0; i<this.fields['intern'].length;i++){
//                if(this.fields['intern.intern'][i].name == 'name_in_japan'){
//                    this.set_field(i,'intern.intern');
//                    break;
//                }
//            }
//            for(var i = 0; i<this.fields['intern.intern'].length;i++){
//                if(this.fields['intern.intern'][i].name == 'date_of_birth'){
//                    this.set_field(i,'intern.intern');
//                     break;
//                }
//            }
            this.$("#report_name")[0].value = "";
        }
        else{
            this.$("#report_name")[0].value = record.name;
        }

        this.record_loaded = $.Deferred();
//        _(this.fields).each(function (field, f) {
//            field._dirty_flag = false;
//            field._inhibit_on_change_flag = true;
//            var result = field.set_value_from_record(self.datarecord);
//            field._inhibit_on_change_flag = false;
//            set_values.push(result);
//        });


        this._actualize_mode(); // call after updating the fields as it may trigger a re-rendering
        this.set({ 'title' : record.id ? record.display_name : _t("New") });
        this.update_pager(); // the mode must be actualized before updating the pager
        return $.when.apply(null, set_values).then(function() {

            self.on_form_changed();

            self.is_initialized.resolve();
            self.record_loaded.resolve();
            if (self.sidebar) {
                self.sidebar.do_attachement_update(self.dataset, self.datarecord.id);
            }
            if (record.id) {
                self.do_push_state({id:record.id});
            } else {
                self.do_push_state({});
            }
//                self.$el.removeClass('oe_form_dirty');
         });
    },

//    load_record: function(){
//        var def = $.Deferred();
//        var self = this;
//        if (this.datarecord.id){
//            var model = new Model('hh.report').call(
//                'read', [[this.datarecord.id]]).then(function (data) {
//                if (data.length) {
//                    self.datarecord = data[0];
//                    if(data[0].field_view){
//                        self.datarecord.field_view = JSON.parse(data[0].field_view);
//                    }
//                    if(data[0].domain){
//                        self.datarecord.domain = JSON.parse(data[0].domain);
//                    }
//                    def.resolve(self.datarecord);
//
//                    self.action_manager.do_push_state({
//                        id: self.datarecord.id,
//                    });
//
//                    self.do_show();
//                    self._actualize_mode('view');
//                    self.toggle_buttons();
//                    self.$('.breadcrumb').append(self._render_breadcrumbs_li(self.datarecord.name,0,1));
//                } else {
//                    self._actualize_mode('edit');
//                    self.toggle_buttons();
//                    self.action_manager.do_push_state({
//                        id: null,
//                    });
//                    def.resolve(null);
//                    self.$('.breadcrumb').append(self._render_breadcrumbs_li('New',0,1));
//                }
//            }).fail(function () {
//                self._actualize_mode('view');
//                self.toggle_buttons();
////                self.action_manager.do_push_state({
////                    id: null,
////                });
//                def.reject();
//            });
//        }
//        else{
//            for(var i = 0; i<this.fields.length;i++){
//                if(this.fields[i].name == 'name'){
//                    this.set_field(i);
//                    break;
//                }
//            }
//            for(var i = 0; i<this.fields.length;i++){
//                if(this.fields[i].name == 'name_in_japan'){
//                    this.set_field(i);
//                    break;
//                }
//            }
//            for(var i = 0; i<this.fields.length;i++){
//                if(this.fields[i].name == 'date_of_birth'){
//                    this.set_field(i);
//                     break;
//                }
//            }
//
//            self.$('.breadcrumb').append(this._render_breadcrumbs_li('New',0,1));
//        }
//
//    },

//    show current record
//    do_show: function(){
//
//    },

    on_form_changed: function() {
        this.trigger("view_content_has_changed");
    },

    do_show: function (options) {
        var self = this;
        options = options || {};
        this.$el.removeClass('oe_form_dirty');

        var shown = this.has_been_loaded;
        if (options.reload !== false) {
            shown = shown.then(function() {
                if (self.dataset.index === null) {
                    // null index means we should start a new record
                    return self.on_button_new();
                }
                var fields = ['name','domain','field_view']
                return self.dataset.read_index(fields, {
                    context: { 'bin_size': true }
                }).then(function(r) {
                    self.trigger('load_record', r);
                });
            });
        }

        return $.when(shown, this._super()).then(function() {
            self._actualize_mode(options.mode || self.options.initial_mode);
            core.bus.trigger('form_view_shown', self);

//            self.$( "#accordion" ).accordion({
//                collapsible: true
//            });
        });
    },

    start: function() {
        var self = this;

//        this.render_buttons( self.$(".top_bar"));

        this.get_fields().then(function (data) {

            self.fields['intern'] = _(data.fields.intern).chain()
            .map(function(val, key) { return _.extend({}, val, {'name': key}); })
            .sortBy(function(field) {return field.string;})
            .value();

            self.fields['internclone'] = _(data.fields.internclone).chain()
            .map(function(val, key) { return _.extend({}, val, {'name': key}); })
            .sortBy(function(field) {return field.string;})
            .value();

            self.fields['invoice'] = _(data.fields.invoice).chain()
            .map(function(val, key) { return _.extend({}, val, {'name': key}); })
            .sortBy(function(field) {return field.string;})
            .value();




            self.$('.o_report_creator_sidebar_main').append($(QWeb.render("hh_hoso.create_report_view.sidebar",
                    {fields_intern:self.fields['intern'],fields_internclone:self.fields['internclone'],
                    fields_invoice:self.fields['invoice']
                    })));

//            self.load_record();

            //Tao selection for date
            var select = $('<select name="options_date" id="options_date"></select>');
             $.each(data.date, function(index, value) {
               var option = $('<option></option>');
               option.attr('value', value[0]);
               option.text(value[1]);
               select.append(option);
             });
             self.$('.selector_date_field').empty().append(select);



             self.has_been_loaded.resolve();
        });

        self.$(".input_date_start").append(this.datewidget_start.$el);
        self.$(".input_date_end").append(this.datewidget_end.$el);


        this.$(".oe_title,.o_group").on('click', function (e) {
            if(self.get("actual_mode") === "view" && self.$buttons && !$(e.target).is('[data-toggle]')) {
                self.$buttons.find(".o_form_button_edit").openerpBounce();
                core.bus.trigger('click', e);
            }
        });


        return this._super();

//        var self = this;
//        this.fields = ["field1","field2"]; //this.get('value');
//        var $content = this.render_content({
//            fields:this.fields
//        })
//
////        this.$(".o_report_creator").html($content.contents());
//        return this._super();
    },

//    render_content: function (options) {
//        return $(QWeb.render("hh_hoso.create_report_view.content", options));
//    },
//    render_sidebar: function () {
//        var self = this;
//        var $sidebar = this._render_sidebar({
//            active_channel_id: this.channel ? this.channel.id: undefined,
//            channels: chat_manager.get_channels(),
//            needaction_counter: chat_manager.get_needaction_counter(),
//            starred_counter: chat_manager.get_starred_counter(),
//        });
//        this.$(".o_report_creator_sidebar").html($sidebar.contents());
//    },
//
//    _render_sidebar: function (options) {
//        return $(QWeb.render("mail.chat.Sidebar", options));
//    },
});

//core.action_registry.add('hh_hoso.create_report', CreateReport);

core.view_registry.add('createreport', CreateReport);

return CreateReport;


});
