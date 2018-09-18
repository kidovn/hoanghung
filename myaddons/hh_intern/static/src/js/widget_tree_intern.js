odoo.define('hh_intern.hh_widget', function (require) {
"use strict";

var ControlPanel = require('web.ControlPanel');
var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var common = require('web.form_common');
var ListView = require('web.ListView');
var ListViewNew = require('hh_intern.ListView');
require('hh_intern.ListEditor'); // one must be sure that the include of ListView are done (for eg: add start_edition methods)
var Model = require('web.DataModel');
var session = require('web.session');
var utils = require('web.utils');
var ViewManager = require('web.ViewManager');
var data_manager = require('web.data_manager');
var pyeval = require('web.pyeval');
var SearchView = require('web.SearchView');

var _t = core._t;
var QWeb = core.qweb;
var FieldMany2Many = core.form_widget_registry.get('many2many');
var FieldOne2Many = core.form_widget_registry.get('one2many');
var FormCustom = require('hh_intern.FormCustom');
var FormView = require('web.FormView');
var One2ManyListView = core.one2many_view_registry.get('list');
var form_relational = require('web.form_relational');
var COMMANDS = common.commands;


//data.DataSetStatic.include({
//    read_slice: function (fields, options) {
//        options = options || {};
//        fields = fields || {};
//        var offset = options.offset || 0,
//            limit = options.limit || false;
//        var end_pos = limit && limit !== -1 ? offset + limit : this.ids.length;
//        return this.read_ids(this.ids.slice(offset, end_pos), fields, options);
//    },
//});

//data.DataSet.include({
//    read_ids: function (ids, fields, options) {
//        if (_.isEmpty(ids))
//            return $.Deferred().resolve([]);
//
//        options = options || {};
//        var method = 'read';
//        var ids_arg = ids;
//        var context = this.get_context(options.context);
//        if (options.check_access_rule === true){
//            method = 'search_read';
//            ids_arg = [['id', 'in', ids]];
//            context = new data.CompoundContext(context, {active_test: false});
//        }
//        if(this.model && this.child_name && this.model=='intern.intern' && this.child_name == "interns_pre"){
//            var tmpId = this.parent_view.datarecord.id;
//
//        }
//        return this._model.call(method,
//                [ids_arg, fields || false],
//                {context: context})
//            .then(function (records) {
//                if (records.length <= 1) { return records; }
//                var indexes = {};
//                for (var i = 0; i < ids.length; i++) {
//                    indexes[ids[i]] = i;
//                }
//                records.sort(function (a, b) {
//                    return indexes[a.id] - indexes[b.id];
//                });
//                return records;
//        });
//    },
//    add_ids: function(ids, at) {
//        var args;
//        /* KIDO HACK WAY  for sequence*/
//        if (this.model == 'intern.intern'){
//            args = [this.ids.length,0].concat(_.difference(ids, this.ids));
//        }
//        else{
//            args = [at, 0].concat(_.difference(ids, this.ids));
//        }
//        this.ids.splice.apply(this.ids, args);
//    },
//});
//
//data.BufferedDataSet.include({
//    add_ids: function(ids, at) {
//        var self = this;
//        this._super(ids, at);
//        _.each(ids, function (id) {
//            self.get_cache(id).to_delete = false;
//        });
//    },
//
//});

ListView.Groups.include({
    passthrough_events: "action deleted row_link \
//                         promote ready_exam delete_from_promote delete_from_exam \
//                         exclude_from_exam set_pass set_preparatory include_to_exam down_to_preparatory \
//                         down_to_cancel_pass up_to_pass up_to_preparatory show_issues show_issue_after_exam show_late_doc \
                         toggle_button_bool toggle_delete_bool toggle_one2many_col",
    init: function (view, options) {
        this._super(view,options);
    },

});

form_relational.AbstractManyField.include({
    data_create_multi: function (datas, options) {
        var commands = [];
        for(var i = 0; i<datas.length;i++){
            commands.push(COMMANDS.create(datas[i]));
        }
        var self = this;
        return this.send_commands(commands, options).then(function(){
            var ids = [];
            for(var index in datas){
                ids.push(datas[index].intern_id[0]);
            }

            var dataset = new data.DataSetStatic(self, 'intern.intern', self.build_context());
//            var fields = self.views[0].fields_view.fields;
            var fields = [];
            for (var index in self.views[0].fields_view.arch.children){
                if(self.views[0].fields_view.arch.children[index].tag == "field"){
                    if(self.views[0].fields_view.arch.children[index].attrs['name']!='intern_id')
                        fields.push(self.views[0].fields_view.arch.children[index].attrs['name']);
                }
            }
//            var fields = _.pluck(_.select(self.views[0].fields_view.arch.children, function(x) {return x.tag == "field";}), 'attrs');
            return dataset.read_ids(ids,fields,{context:{bin_size:true}}).then(function (records) {
                if (_.isEmpty(records)) { return $.Deferred().reject().promise(); }
                for(var index in records){
                    for(var id in self.dataset.cache){
                        if(self.dataset.cache[id].values.intern_id[0] ==  records[index].id && !self.dataset.cache[id].to_delete){
                            records[index].intern_id = self.dataset.cache[id].values.intern_id;
                            records[index].id = self.dataset.cache[id].values.id;
                            for(var field in fields){
                                if(!records[index][fields[field]]){
                                    records[index][fields[field]] = undefined;
                                }
                            }
//                            self.dataset.cache[id].values = records[index];
                            self.dataset._update_cache(id,{from_read:records[index]});
                            break;
                        }
                    }
                }
                return records[0];
            });
        });
    },

});
var X2ManyListNew = ListView.List.extend({

    init: function (group, opts) {
        this._super(group, opts);
        var self = this;
        this.records = opts.records;
        this.$current.undelegate('td button', 'click');
        this.$current.delegate('.o_bool_button','click',function(e){
                e.stopPropagation();
                var $target = $(e.currentTarget),
                      field = $target.closest('td').data('field'),
                       $row = $target.closest('tr'),
                  record_id = $($row).data('id');
                   var context = self.view.fields_view.fields[field].__attrs.context;
                 $(self).trigger('toggle_button_bool',[record_id,field,context]);
            }).delegate('.bool_delete','click',function(e){
                e.stopPropagation();
                var $target = $(e.currentTarget),
                      field = $target.closest('td').data('field'),
                       $row = $target.closest('tr'),
                  record_id = $($row).data('id');
                var context = self.view.fields_view.fields[field].__attrs.context;
                $(self).trigger('toggle_delete_bool',[record_id,field,context]);

            }).delegate('.o_bool_button_reverse','click',function(e){
                e.stopPropagation();
                var $target = $(e.currentTarget),
                      field = $target.closest('td').data('field'),
                       $row = $target.closest('tr'),
                  record_id = $($row).data('id');
                  var context = self.view.fields_view.fields[field].__attrs.context;
                 $(self).trigger('toggle_button_bool',[record_id,field,context]);
            }).delegate('.o_one2many_col','click',function(e){
                e.stopPropagation();
                var $target = $(e.currentTarget),
                      field = $target.closest('td').data('field'),
                       $row = $target.closest('tr'),
                record_id = $($row).data('id');
                var context = self.view.fields_view.fields[field].__attrs.context;
                $(self).trigger('toggle_one2many_col',[record_id,field,context]);
            }).delegate('.o_bool_button_extend','click',function(e){
                e.stopPropagation();
                var $target = $(e.currentTarget),
                      field = $target.closest('td').data('field'),
                       $row = $target.closest('tr'),
                  record_id = $($row).data('id');
                   var context = self.view.fields_view.fields[field].__attrs.context;
                  $.when($(self).trigger('toggle_one2many_col',[record_id,field,context])).done(function(){
                        $(self).trigger('toggle_button_bool',[record_id,field,context]);
                  });
            })
            ;
    },

    render_cell: function (record, column) {
        if(column.options_tmp  && column.options_tmp.invisible_content){
            for(var condition in column.options_tmp.invisible_content){
                var tmp = ""+record.attributes[condition];
                if (column.options_tmp.invisible_content[condition]== tmp){
                    return "";
                }
            }
        }
        var value;
        if(column.type === 'reference') {
            value = record.get(column.id);
            var ref_match;
            // Ensure that value is in a reference "shape", otherwise we're
            // going to loop on performing name_get after we've resolved (and
            // set) a human-readable version. m2o does not have this issue
            // because the non-human-readable is just a number, where the
            // human-readable version is a pair
            if (value && (ref_match = /^([\w\.]+),(\d+)$/.exec(value))) {
                // reference values are in the shape "$model,$id" (as a
                // string), we need to split and name_get this pair in order
                // to get a correctly displayable value in the field
                var model = ref_match[1],
                    id = parseInt(ref_match[2], 10);
                new data.DataSet(this.view, model).name_get([id]).done(function(names) {
                    if (!names.length) { return; }
                    record.set(column.id + '__display', names[0][1]);
                });
            }
        } else if (column.type === 'many2one') {
            value = record.get(column.id);
            // m2o values are usually name_get formatted, [Number, String]
            // pairs, but in some cases only the id is provided. In these
            // cases, we need to perform a name_get call to fetch the actual
            // displayable value
            if (typeof value === 'number' || value instanceof Number) {
                // fetch the name, set it on the record (in the right field)
                // and let the various registered events handle refreshing the
                // row
                new data.DataSet(this.view, column.relation)
                        .name_get([value]).done(function (names) {
                    if (!names.length) { return; }
                    record.set(column.id, names[0]);
                });
            }
        } else if (column.type === 'many2many') {
            value = record.get(column.id);
            // non-resolved (string) m2m values are arrays
            if (value instanceof Array && !_.isEmpty(value)
                    && !record.get(column.id + '__display')) {
                var ids;
                // they come in two shapes:
                if (value[0] instanceof Array) {
                    _.each(value, function(command) {
                        switch (command[0]) {
                            case 4: ids.push(command[1]); break;
                            case 5: ids = []; break;
                            case 6: ids = command[2]; break;
                            default: throw new Error(_.str.sprintf( _t("Unknown m2m command %s"), command[0]));
                        }
                    });
                } else {
                    // 2. an array of ids
                    ids = value;
                }
                new Model(column.relation)
                    .call('name_get', [ids, this.dataset.get_context()]).done(function (names) {
                        // FIXME: nth horrible hack in this poor listview
                        record.set(column.id + '__display',
                                   _(names).pluck(1).join(', '));
                        record.set(column.id, ids);
                    });
                // temporary empty display name
                record.set(column.id + '__display', false);
            }
        }

        if(column.options_tmp && column.options_tmp.merge_field){
            var main = column.format(record.toForm().data, {
                model: this.dataset.model,
                id: record.get('id'),
                options: this.options   //KIDO hack more option for column
            });
            var add_field = this.columns[column.options_tmp.merge_field].format(record.toForm().data, {
                model: this.dataset.model,
                id: record.get('id'),
                options: this.options   //KIDO hack more option for column
            });
            if(add_field!="&nbsp;"){
                return main +"<br/><span style='color:red;font-size: 10px;'>"+ add_field +"</span>";
            }
            else{
                return main;
            }
        }
        return column.format(record.toForm().data, {
            model: this.dataset.model,
            id: record.get('id'),
            options: this.options   //KIDO hack more option for column
        });
    },

    render: function () {
        var self = this;
        this.$current.html(
            QWeb.render('ListViewNew.rowsnew', _.extend({}, this, {
                    should_visible:function(index){
                        if(self.view.x2m.name == 'interns_promoted'){
                            if(self.records.records[index].attributes.promoted){
                                return true;
                            }
                            return false;
                        }
                        else if(self.view.x2m.name=='interns_confirm_exam'){
                            if(self.records.records[index].attributes.confirm_exam && !self.records.records[index].attributes.issues_raise){
                                return true;
                            }
                            return false;
                        }
                        else if(self.view.x2m.name=='interns_escape_exam'){
                            if(self.records.records[index].attributes.confirm_exam && self.records.records[index].attributes.issues_raise){
                                return true;
                            }
                            return false;
                        }
                        else if(self.view.x2m.name=='interns_pass_new'){
                            if(self.records.records[index].attributes.pass_exam && !self.records.records[index].attributes.cancel_pass){
                                return true;
                            }
                            return false;
                        }
                        else if(self.view.x2m.name=='interns_preparatory')
                        {
                            if(self.records.records[index].attributes.preparatory_exam && !self.records.records[index].attributes.cancel_pass){
                                return true;
                            }
                            return false;
                        }
                        else if(self.view.x2m.name=='interns_cancel_pass')
                        {
                            if(self.records.records[index].attributes.cancel_pass){
                                return true;
                            }
                            return false;
                        }
                        else if(self.view.x2m.name=='interns_departure')
                        {
                            if(self.records.records[index].attributes.departure){
                                return true;
                            }
                            return false;
                        }
                        return true;
                    },
                    deletable: function(){
                        return self.deletable.apply(self,arguments);
                    },
                    show_column:function(column){
                        if(column.options_tmp  && column.options_tmp.invisible){
                            for(var condition in column.options_tmp.invisible){
                                if ('datarecord' in self.view.x2m.getParent() && column.options_tmp.invisible[condition].indexOf(self.view.x2m.getParent().datarecord[condition])>-1){
                                    return false;
                                }
                            }
                            return true;

                        }
                        return true;
                    },
                    render_cell: function () {
                        return self.render_cell.apply(self, arguments); },


                },  )));

            this.pad_table_to(4);
    },



    deletable: function (record){
        var context = this.dataset.get_context();
        var parent = this.group.view.ViewManager.x2m.getParent().fields;
        var id = record.get('id');
        if(this.view.x2m.name=='interns_clone'){
            if(context.__contexts && context.__contexts.length>0 && context.__contexts[0].length>0 && context.__contexts[0].includes("'page':'promotion'")){
                if(!this.dataset.cache[id].values.promoted){
                    return true;
                }
            }
        }
        else if(this.view.x2m.name=='interns_promoted'){
            if(context.__contexts && context.__contexts.length>0 && context.__contexts[0].length>0 && context.__contexts[0].includes("'page':'promotion'")){
                var parentTmp = this.group.view.ViewManager.x2m.getParent();
                if (parentTmp.datarecord.status ==4){
                    return false;
                }
            }
            //KIDO xoa khi remove quyen cua doingoai
            else if(context.__contexts && context.__contexts.length>0 && context.__contexts[0].length>0 && context.__contexts[0].includes("'page':'doingoai'")){
                var parentTmp = this.group.view.ViewManager.x2m.getParent();
                if (parentTmp.datarecord.status ==5){
                    return true;
                }
            }
        }
//        else if(this.view.x2m.name == 'interns_confirm_exam'){
//            if(context.__contexts && context.__contexts.length>0 && context.__contexts[0].length>0 && context.__contexts[0].includes("'page':'doingoai'")){
//                var parentTmp = this.group.view.ViewManager.x2m.getParent();
//                if (parentTmp.datarecord.status ==5 || parentTmp.datarecord.status==1){
//                    return true;
//                }
//            }
//
//        }

        return false;
    },



    pad_table_to: function (count) {
        if (!this.view.is_action_enabled('create') || this.view.x2m.get('effective_readonly')) {
            if (this.records.length >= count ||
                _(this.columns).any(function(column) { return column.meta; })) {
                return;
            }
            var cells = [];
            cells.push('<td/>');
            if (this.options.selectable) {
                cells.push('<td class="o_list_record_selector"></td>');
            }
            _(this.columns).each(function(column) {
                if (column.invisible === '1') {
                    return;
                }
                cells.push('<td title="' + column.string + '">&nbsp;</td>');
            });
            if (this.options.deletable) {
                cells.push('<td class="o_list_record_delete"></td>');
            }
            cells.unshift('<tr>');
            cells.push('</tr>');

            var row = cells.join('');
            this.$current
                .children('tr:not([data-id])').remove().end()
                .append(new Array(count - this.records.length + 1).join(row));

            return
        }

        this._super(count > 0 ? count - 1 : 0);

        var self = this;
        var columns = _(this.columns).filter(function (column) {
            return column.invisible !== '1';
        }).length;
        if (this.options.selectable) { columns++; }
        if (this.options.deletable) { columns++; }
        columns++;

        var $cell = $('<td>', {
            colspan: columns,
            'class': 'o_form_field_x2many_list_row_add'
        }).append(
            $('<a>', {href: '#'}).text(_t("Add an item"))
                .click(function (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    var def;
                    if (self.view.editable()) {
                        // FIXME: there should also be an API for that one
                        if (self.view.editor.form.__blur_timeout) {
                            clearTimeout(self.view.editor.form.__blur_timeout);
                            self.view.editor.form.__blur_timeout = false;
                        }
                        def = self.view.save_edition();
                    }
                    $.when(def).done(self.view.do_add_record.bind(self));
                }));

        var $padding = this.$current.find('tr:not([data-id]):first');
        var $newrow = $('<tr>').append($cell);
        if ($padding.length) {
            $padding.before($newrow);
        } else {
            this.$current.append($newrow);
        }
    },

    render_record: function (record) {
        var self = this;
        var index = this.records.indexOf(record);
        return QWeb.render('ListViewNew.row', {
            columns: this.columns,
            options: this.options,
            record: record,
            row_parity: (index % 2 === 0) ? 'even' : 'odd',
            view: this.view,
            render_cell: function () {
                return self.render_cell.apply(self, arguments); },

            show_column: function(column){
                if(column.options_tmp  && column.options_tmp.invisible){
                    for(var condition in column.options_tmp.invisible){
                        if (self.ViewManager!== undefined && column.options_tmp.invisible[condition].indexOf(self.ViewManager.x2m.getParent().datarecord[condition])>-1){
                            return false;
                        }
                    }
                    return true;

                }
                return true;
            },
            deletable: function(){
                return self.deletable.apply(self,arguments);
            },
        });
    }

});


var X2ManyListViewNew = ListViewNew.extend({

    is_valid: function () {
        if (!this.fields_view || !this.editable()){
            return true;
        }
        if (_.isEmpty(this.records.records)){
            return true;
        }
        var fields = this.editor.form.fields;
        var current_values = {};
        _.each(fields, function(field){
            field._inhibit_on_change_flag = true;
            field.__no_rerender = field.no_rerender;
            field.no_rerender = true;
            current_values[field.name] = field.get('value');
        });
        var ids = _.map(this.records.records, function (item) { return item.attributes.id; });
        var cached_records = _.filter(this.dataset.cache, function(item){return _.contains(ids, item.id) && !_.isEmpty(item.values) && !item.to_delete;});
        var valid = _.every(cached_records, function(record){
            _.each(fields, function(field){
                var value = record.values[field.name];
                field._inhibit_on_change_flag = true;
                field.no_rerender = true;
                field.set_value(_.isArray(value) && _.isArray(value[0]) ? [COMMANDS.delete_all()].concat(value) : value);
            });
            return _.every(fields, function(field){
                field.process_modifiers();
                field._check_css_flags();
                return field.is_valid();
            });
        });
        _.each(fields, function(field){
            field.set('value', current_values[field.name], {silent: true});
            field._inhibit_on_change_flag = false;
            field.no_rerender = field.__no_rerender;
        });
        return valid;
    },
    render_pager: function($node, options) {
        options = _.extend(options || {}, {
            single_page_hidden: true,
        });
        this._super($node, options);
    },
    display_nocontent_helper: function () {
        return false;
    },
});






var FieldMany2ManyIntern = FieldMany2Many.extend({
    init: function() {
        this._super.apply(this, arguments);
        this.x2many_views = {
            list: Many2ManyListViewNew,
            kanban: core.view_registry.get('many2many_kanban'),
        };
//        this.on("link_external", this, function(id){
//            alert(id);
//        });
        if(this.name == 'interns_promoted'|| this.name=='interns_confirm_exam' || this.name=='interns_escape_exam'
            || this.name=='interns_pass_new'  || this.name=='interns_preparatory'  || this.name=='interns_cancel_pass'
            || this.name=='interns_departure'){
            this.dataset = this.getParent().fields.interns_clone.dataset;
        }
    },
    start: function() {
        this.$el.addClass('o_form_field_many2many_intern');
        return this._super.apply(this, arguments);
    },


    promote: function(id){
        this.dataset.write(id,{promoted:true});
        this.reload_current_view();
    },

    //KIDO toggle button bool
    toggle_button_bool:function(id, field,options){
        var values = {};
        values[field] = !this.dataset.cache[id].values[field];
        if(options){
            var options_tmp = pyeval.py_eval(options);
            for (var t in options_tmp.related)
                values[options_tmp.related[t]] = false;
        }
        this.dataset.write(id,values,{});
        if(this.getParent().fields.interns_clone)
            this.getParent().fields.interns_clone.reload_current_view();
        if(this.getParent().fields.interns_promoted)
            this.getParent().fields.interns_promoted.reload_current_view();
        if(this.getParent().fields.interns_confirm_exam)
            this.getParent().fields.interns_confirm_exam.reload_current_view();
        if(this.getParent().fields.interns_escape_exam)
            this.getParent().fields.interns_escape_exam.reload_current_view();
        if(this.getParent().fields.interns_pass_new)
            this.getParent().fields.interns_pass_new.reload_current_view();
        if(this.getParent().fields.interns_preparatory)
            this.getParent().fields.interns_preparatory.reload_current_view();
        if(this.getParent().fields.interns_cancel_pass)
            this.getParent().fields.interns_cancel_pass.reload_current_view();
        if(this.getParent().fields.interns_departure)
            this.getParent().fields.interns_departure.reload_current_view();
    },

    toggle_delete_bool:function(id,field,options){

        var values = {};
        values[field] = false;
        if(options){
            var options_tmp = pyeval.py_eval(options);
            for (var t in options_tmp.related)
                values[options_tmp.related[t]] = false;
        }
        this.dataset.write(id,values,{});
        if(this.getParent().fields.interns_clone)
            this.getParent().fields.interns_clone.reload_current_view();
        if(this.getParent().fields.interns_promoted)
            this.getParent().fields.interns_promoted.reload_current_view();
        if(this.getParent().fields.interns_confirm_exam)
            this.getParent().fields.interns_confirm_exam.reload_current_view();
        if(this.getParent().fields.interns_escape_exam)
            this.getParent().fields.interns_escape_exam.reload_current_view();
        if(this.getParent().fields.interns_pass_new)
            this.getParent().fields.interns_pass_new.reload_current_view();
        if(this.getParent().fields.interns_preparatory)
            this.getParent().fields.interns_preparatory.reload_current_view();
        if(this.getParent().fields.interns_cancel_pass)
            this.getParent().fields.interns_cancel_pass.reload_current_view();
        if(this.getParent().fields.interns_departure)
            this.getParent().fields.interns_departure.reload_current_view();
    },
});

var X2ManyDataSet = data.BufferedDataSet.extend({
    get_context: function() {
        this.context = this.x2m.build_context();
        var self = this;
        _.each(arguments, function(context) {
            self.context.add(context);
        });
        return this.context;
    },
});



var FormViewDialogSpecific = common.ViewDialog.extend({

    init: function(parent, options) {
        this.intern_id = options.intern_id;
        this._super(parent, options);
    },

    open: function() {

        var _super = this._super.bind(this);
        var parent = this.getParent().ViewManager.x2m.getParent();
        var tmpset;
        if(this.options.res_model == 'intern.issueafter'){
            tmpset = parent.fields.issues_after_exam.dataset;
        }
        else{
            tmpset = parent.fields.issues.dataset;
        }
        this.dataset = new X2ManyDataSet(this, this.options.res_model, {});
        var arrayIds = [];
        for(var i = 0; i<tmpset.ids.length;i++){
            var tmpCache = tmpset.cache[tmpset.ids[i]];
            if(!tmpCache.to_delete){
                if(tmpCache.values.intern_id == this.intern_id){
                    arrayIds.push(tmpCache.id);
                    this.dataset.cache[tmpCache.id] = tmpCache;
                }
            }
        }
        this.dataset.ids= arrayIds;
        if(this.options.res_model == 'intern.issueafter'){
            this.dataset.x2m =parent.fields.issues_after_exam.dataset.x2m;
            this.dataset.parent_view = parent.fields.issues_after_exam.dataset.parent_view;
            this.dataset.child_name = parent.fields.issues_after_exam.dataset.child_name;
        }
        else{
            this.dataset.x2m =parent.fields.issues.dataset.x2m;
            this.dataset.parent_view = parent.fields.issues.dataset.parent_view;
            this.dataset.child_name = parent.fields.issues.dataset.child_name;
        }

        var context = pyeval.sync_eval_domains_and_contexts({
            domains: [],
            contexts: [this.context]
        }).context;
        var search_defaults = {};
        _.each(context, function (value_, key) {
            var match = /^search_default_(.*)$/.exec(key);
            if (match) {
                search_defaults[match[1]] = value_;
            }
        });
        data_manager
            .load_views(this.dataset, [[false, 'list'], [false, 'search']], {})
            .then(this.setup.bind(this, search_defaults))
            .then(function (fragment) {
                _super().$el.append(fragment);
            });
        return this;
    },
    setup: function(search_defaults, fields_views) {
        var self = this;
        var fragment = document.createDocumentFragment();
        var $header = $('<div/>').addClass('o_modal_header').appendTo(fragment);
        var $pager = $('<div/>').addClass('o_pager').appendTo($header);

            self.view_list = new One2ManyListView(self,
                self.dataset, fields_views.list,
                _.extend({'deletable': this.options.deletable,
                    'selectable': false,
                    'import_enabled': false,
                    '$buttons': self.$buttons,
                    'disable_editable_mode': false,
                    'pager': false,

                }, self.options.list_view_options || {}));
            if(this.options.res_model == 'intern.issueafter'){
                self.view_list.x2m = self.getParent().ViewManager.x2m.getParent().fields.issues_after_exam.viewmanager.x2m;
            }
            else
                self.view_list.x2m = self.getParent().ViewManager.x2m.getParent().fields.issues.viewmanager.x2m;
            self.view_list.popup = self;
            self.view_list.on('list_view_loaded', self, function() {
                this.on_view_list_loaded();
            });

            var buttons = [
                {text: _t("Close"), classes: "btn-default o_form_button_cancel", close: true}
            ];

            self.set_buttons(buttons);

            return self.view_list.appendTo(fragment).then(function() {
                self.view_list.do_show();
                self.view_list.reload_content();
                return fragment;
            });
    },

    destroy: function(reason) {
        var parent = this.getParent().ViewManager.x2m.getParent();
        var tmpset;
        if(this.options.res_model == 'intern.issueafter'){
            tmpset = parent.fields.issues_after_exam.dataset;
        }
        else{
            tmpset = parent.fields.issues.dataset;
        }
        var idscache = Object.keys(this.dataset.cache);
        for(var i = 0; i<idscache.length;i++){

            var id = idscache[i];
            var tmpCache = this.dataset.cache[id];
            if(tmpCache.to_delete){
                var index = tmpset.ids.indexOf(tmpCache.id);
                if(index>-1){
                    tmpset.ids.splice(index, 1);
                }
            }
            else{
                tmpCache.values.intern_id = this.intern_id;
                tmpCache.changes.intern_id= this.intern_id;
                if(typeof id === 'string' && id.startsWith("one2many") && tmpset.cache[id]== undefined ){
                    tmpset.ids.push(id);
                }
            }
            tmpset.cache[id] = tmpCache;

        }
        this._super();
    },

    on_view_list_loaded: function() {},

    create_edit_record: function() {
        this.close();
        return new common.FormViewDialog(this.__parentedParent, this.options).open();
    },
});

var One2ManyGroups = ListView.Groups.extend({
    setup_resequence_rows: function () {
        if (!this.view.x2m.get('effective_readonly')) {
            this._super.apply(this, arguments);
        }
    }
});


var Many2ManyListViewNew = X2ManyListViewNew.extend({
    init: function () {
        this._super.apply(this, arguments);
        this.options = _.extend(this.options, {
            ListType: X2ManyListNew,
        });
        this.on('edit:after', this, this.proxy('_after_edit'));
        this.on('save:before cancel:before', this, this.proxy('_before_unedit'));
    },


    do_add_record: function () {
        var self = this;
        var model = this.model;
        if(this.model == 'intern.internclone'){
            model = 'intern.intern';
        }
        var ids = [];
        if(self.model == 'intern.internclone'){
            for(var key in this.x2m.dataset.cache){
                if(!this.x2m.dataset.cache[key].to_delete){
                    ids.push(this.x2m.dataset.cache[key].values.intern_id[0]);
                }
            }
        }
        else{
            ids = this.x2m.dataset.ids
        }

        new common.SelectCreateDialog(this, {
            res_model: model,
            domain: new data.CompoundDomain(this.x2m.build_domain(), ["!", ["id", "in", ids]]),
            context: this.x2m.build_context(),
            title: _t("Add: ") + this.x2m.string,
            alternative_form_view: this.x2m.field.views ? this.x2m.field.views.form : undefined,
            no_create: this.x2m.options.no_create || !this.is_action_enabled('create'),
            on_selected: function(element_ids) {
                if(self.model == 'intern.internclone'){
                    var datas = [];
                    for(var i = 0; i<element_ids.length;i++){
                        //KIDO should remove when remove dn right
                        if(self.ViewManager.x2m.name == 'interns_promoted'){
                            datas.push({intern_id:[element_ids[i],'TESTTHU'],promoted:true});
                        }
                        else{
                            datas.push({intern_id:[element_ids[i],'TESTTHU']});
                        }
                    }
                    if(self.ViewManager.x2m.name == 'interns_promoted'){
                        return self.getParent().getParent().getParent().fields.interns_clone.viewmanager.x2m.data_create_multi(datas,{}).then(function(){

                            self.getParent().getParent().getParent().fields.interns_clone.update_to_other();
                        });
                    }
                    else{
                        return self.x2m.data_create_multi(datas,{}).then(function(){

                            self.x2m.reload_current_view();
                        });
                    }
                }
                return self.x2m.data_link_multi(element_ids).then(function() {
                    self.x2m.reload_current_view();
                });
            }
        }).open();
    },

    do_show_issue_after_exam:function(record_id){
        var self = this;
        var id = self.ViewManager.x2m.getParent().datarecord.id;
        var model = self.ViewManager.x2m.getParent().model;

        var context = self.dataset.get_context();
        var is_kiemsoat = false;
        if(context.__contexts && context.__contexts.length>0 && context.__contexts[0].length>0 && context.__contexts[0].includes("'page':'kiemsoat'")){
            is_kiemsoat = true;
        }

        var pop = new FormViewDialogSpecific(this, {
            res_model: 'intern.issueafter',
            res_id: id,
            intern_id: record_id,
            context: "{'tree_view_ref':'hh_intern.view_ks_invoice_issues_after_exam_tree','intern_id':"+record_id+"}",
            title: _t("Open: ") + "Phát sinh của TTS sau thi tuyển",
            deletable:this.options.deletable,
            alternative_form_view: undefined,
            readonly: !is_kiemsoat || !this.is_action_enabled('edit') || self.x2m.get("effective_readonly") ,
        }).open();
        pop.on('write_completed', self, function () {
            self.dataset.evict_record(id);
            self.reload_content();
        });
    },
    do_show_issues: function(record_id){
        var self = this;
        var id = self.ViewManager.x2m.getParent().datarecord.id;
        var model = self.ViewManager.x2m.getParent().model;
        var pop = new FormViewDialogSpecific(this, {
            res_model: 'intern.issue',
            res_id: id,
            intern_id: record_id,
            context: "{'tree_view_ref':'hh_intern.view_ks_invoice_issues_tree','intern_id':"+record_id+"}",
            title: _t("Open: ") + "Phát sinh của TTS trước thi tuyển",
            deletable:this.options.deletable,
            alternative_form_view: undefined,
            readonly: !this.is_action_enabled('edit') || self.x2m.get("effective_readonly"),
        }).open();
        pop.on('write_completed', self, function () {
            self.dataset.evict_record(id);
            self.reload_content();
        });
    },
    do_show_late_doc: function(record_id){

        var parent = this.x2m.getParent().fields.late_doc;
        var id = undefined;
        var cache_record = undefined;
        if(parent){
            var cachekey = Object.keys(parent.dataset.cache);
            for(var tmp = 0; tmp<cachekey.length;tmp++){
                if(parent.dataset.cache[cachekey[tmp]].values.intern_id == record_id){
                    if(!parent.dataset.cache[cachekey[tmp]].to_delete){
                        id = parent.dataset.cache[cachekey[tmp]].id;
                        cache_record = parent.dataset.cache[cachekey[tmp]].values;
                        cache_record.id = id;
                    }
                    break;
                }
            }
        }
        var readonly = !this.is_action_enabled('edit') || this.x2m.get("effective_readonly");
        if(id == undefined){
            if(readonly){
                return;
            }
            else{
                var self = this.x2m.getParent().fields.late_doc.viewmanager;
                new FormCustom.SelectCreateDialogCustom(self, {
                    res_model: self.x2m.field.relation,
                    domain: self.x2m.build_domain(),
                    context: self.x2m.build_context(),
                    title: _t("Create: ") + self.x2m.string,
                    initial_view: "form",
                    alternative_form_view: self.x2m.field.views ? self.x2m.field.views.form : undefined,
                    create_function: function(data, options) {
                        return self.x2m.data_create(data, options);
                    },
                    read_function: function(ids, fields, options) {
                        return self.x2m.data_read(ids, fields, options);
                    },
                    parent_view: self.x2m.view,
                    child_name: self.x2m.name,
                    form_view_options: {'not_interactible_on_create':true},
                    default_value:{invoice_id:this.x2m.getParent().datarecord.id,intern_id:record_id},
                    disable_multiple_selection:true,
                    on_selected: function() {
                        self.x2m.reload_current_view();
                    }
                }).open();
            }
        }
        else{
            var self = this.x2m.getParent().fields.late_doc.viewmanager;
            new common.FormViewDialog(self, {
                res_model: self.x2m.field.relation,
                res_id: id,
                context: self.x2m.build_context(),
                title: _t("Open: ") + self.x2m.string,
                write_function: function(id, data, options) {
                    return self.x2m.data_update(id, data, options).done(function() {
                        self.x2m.reload_current_view();
                    });
                },
                alternative_form_view: self.x2m.field.views ? self.x2m.field.views.form : undefined,
                parent_view: self.x2m.view,
                child_name: self.x2m.name,
                read_function: function(ids, fields, options) {
                    return self.x2m.data_read(ids, fields, options);
                },
                form_view_options: {'not_interactible_on_create':true},
                readonly: !this.is_action_enabled('edit') || self.x2m.get("effective_readonly")
            }).open();
        }

    },
    do_activate_record: function(index, id) {
        var self = this;
        var pop = new common.FormViewDialog(this, {
            res_model: this.model,
            res_id: id,
            context: this.x2m.build_context(),
            title: _t("Open: ") + this.x2m.string,
            alternative_form_view: this.x2m.field.views ? this.x2m.field.views.form : undefined,
            readonly: !this.is_action_enabled('edit') || self.x2m.get("effective_readonly"),
        }).open();
        pop.on('write_completed', self, function () {
            self.dataset.evict_record(id);
            self.reload_content();
        });
    },

    do_button_action: function(name, id, callback) {
        var self = this;
        var _sup = _.bind(this._super, this);
        if (! this.x2m.options.reload_on_button) {
            return _sup(name, id, callback);
        } else {
            return this.x2m.view.save().then(function() {
                return _sup(name, id, function() {
                    self.x2m.view.reload();
                });
            });
        }
    },
    _after_edit: function () {
        this.editor.form.on('blurred', this, this._on_blur_many2many);
    },
    _before_unedit: function () {
        this.editor.form.off('blurred', this, this._on_blur_many2many);
    },
    _on_blur_many2many: function() {
        return this.save_edition().done(function () {
            if (self._dataset_changed) {
                self.dataset.trigger('dataset_changed');
            }
        });
    },

});

var One2ManyListViewNew = X2ManyListViewNew.extend({
    init: function () {
        this._super.apply(this, arguments);
        this.options = _.extend(this.options, {
            GroupsType: One2ManyGroups,
            ListType: X2ManyListNew
        });
        this.on('edit:after', this, this.proxy('_after_edit'));
        this.on('save:before cancel:before', this, this.proxy('_before_unedit'));

        /* detect if the user try to exit the one2many widget */
        core.bus.on('click', this, this._on_click_outside);

        this.dataset.on('dataset_changed', this, function () {
            this._dataset_changed = true;
            this.dataset.x2m._dirty_flag = true;
        });
        this.dataset.x2m.on('load_record', this, function () {
            this._dataset_changed = false;
        });

        this.on('warning', this, function(e) { // In case of editable list view, we do not want any warning which comes from the editor
            if (this.editable()) {
                e.stop_propagation();
            }
        });
    },
    do_add_record: function () {
//        if (this.editable()) {
//            this._super.apply(this, arguments);
//        } else {
            var self = this;

//            var self = this;
            var model = this.model;
            if(this.model == 'intern.internclone'){
                model = 'intern.intern';
            }
            var ids = [];
            if(self.model == 'intern.internclone'){
                for(var key in this.x2m.dataset.cache){
                    if(!this.x2m.dataset.cache[key].to_delete){
                        ids.push(this.x2m.dataset.cache[key].values.intern_id[0]);
                    }
                }
            }
            else{
                ids = this.x2m.dataset.ids
            }

            new common.SelectCreateDialog(this, {
                res_model: model,
                domain: new data.CompoundDomain(this.x2m.build_domain(), ["!", ["id", "in", ids]]),
                context: this.x2m.build_context(),
                title: _t("Add: ") + this.x2m.string,
                alternative_form_view: this.x2m.field.views ? this.x2m.field.views.form : undefined,
                no_create: this.x2m.options.no_create || !this.is_action_enabled('create'),
                on_selected: function(element_ids) {
                    if(self.model == 'intern.internclone'){
                        var datas = [];
                        for(var i = 0; i<element_ids.length;i++){
                            //KIDO should remove when remove dn right
                            if(self.ViewManager.x2m.name == 'interns_promoted'){
                                datas.push({intern_id:[element_ids[i],'TESTTHU'],promoted:true});
                            }
                            else{
                                datas.push({intern_id:[element_ids[i],'TESTTHU']});
                            }
                        }
                        if(self.ViewManager.x2m.name == 'interns_promoted'){
                            return self.getParent().getParent().getParent().fields.interns_clone.viewmanager.x2m.data_create_multi(datas,{}).then(function(){

                                self.getParent().getParent().getParent().fields.interns_clone.update_to_other();
                            });
                        }
                        else{
                            return self.x2m.data_create_multi(datas,{}).then(function(){

                                self.x2m.reload_current_view();
                            });
                        }
                    }
                    return self.x2m.data_link_multi(element_ids).then(function() {
                        self.x2m.reload_current_view();
                    });
                }
            }).open();

    },
    do_activate_record: function(index, id) {
        var self = this;
        new common.FormViewDialog(self, {
            res_model: self.x2m.field.relation,
            res_id: id,
            context: self.x2m.build_context(),
            title: _t("Open: ") + self.x2m.string,
            write_function: function(id, data, options) {
                return self.x2m.data_update(id, data, options).done(function() {
                    self.x2m.reload_current_view();
                });
            },
            alternative_form_view: self.x2m.field.views ? self.x2m.field.views.form : undefined,
            parent_view: self.x2m.view,
            child_name: self.x2m.name,
            read_function: function(ids, fields, options) {
                return self.x2m.data_read(ids, fields, options);
            },
            form_view_options: {'not_interactible_on_create':true},
            readonly: !this.is_action_enabled('edit') || self.x2m.get("effective_readonly")
        }).open();
    },
     toggle_one2many_col:function(id,field,context){
        var self = this;
        new common.FormViewDialog(self, {
            res_model: self.x2m.field.relation,
            res_id: id,
            context: context,
            title: _t("Open: "),
            write_function: function(id, data, options) {
                return self.x2m.data_update(id, data, options).done(function() {
                    self.x2m.reload_current_view();
                });
            },
            alternative_form_view: self.x2m.field.views ? self.x2m.field.views.form : undefined,
            parent_view: self.x2m.view,
            child_name: self.x2m.name,
            read_function: function(ids, fields, options) {
                return self.x2m.data_read(ids, fields, options);
            },
            form_view_options: {'not_interactible_on_create':true},
            readonly: !this.is_action_enabled('edit') || self.x2m.get("effective_readonly")
        }).open();
    },

    do_button_action: function (name, id, callback) {
        if (!_.isNumber(id)) {
            this.do_warn(_t("Action Button"),
                         _t("The o2m record must be saved before an action can be used"));
            return;
        }
        var parent_form = this.x2m.view;
        var self = this;
        this.save_edition().then(function () {
            if (parent_form) {
                return parent_form.save();
            } else {
                return $.when();
            }
        }).done(function () {
            var ds = self.x2m.dataset;
            var changed_records = _.find(ds.cache, function(record) {
                return record.to_create || record.to_delete || !_.isEmpty(record.changes);
            });
            if (!self.x2m.options.reload_on_button && !changed_records) {
                self.handle_button(name, id, callback);
            } else {
                self.handle_button(name, id, function(){
                    self.x2m.view.reload();
                });
            }
        });
    },
    start_edition: function (record, options) {
        if (!this.__focus) {
            this._on_focus_one2many();
        }
        return this._super(record, options);
    },
    reload_content: function () {
        var self = this;
        if (self.__focus) {
            self._on_blur_one2many();
            return this._super().then(function () {
                var record_being_edited = self.records.get(self.editor.form.datarecord.id);
                if (record_being_edited) {
                    self.start_edition(record_being_edited);
                }
            });
        }
        return this._super();
    },
    _on_focus_one2many: function () {
        if(!this.editor.is_editing()) {
            return;
        }
        this.dataset.x2m.internal_dataset_changed = true;
        this._dataset_changed = false;
        this.__focus = true;
    },
    _on_click_outside: function(e) {
        if(this.__ignore_blur || !this.editor.is_editing()) {
            return;
        }

        var $target = $(e.target);

        // If click on a button, a ui-autocomplete dropdown or modal-backdrop, it is not considered as a click outside
        var click_outside = ($target.closest('.ui-autocomplete,.btn,.modal-backdrop').length === 0);

        // Check if click inside the current list editable
        var $o2m = $target.closest(".o_list_editable");
        if($o2m.length && $o2m[0] === this.el) {
            click_outside = false;
        }

        // Check if click inside a modal which is on top of the current list editable
        var $modal = $target.closest(".modal");
        if($modal.length) {
            var $currentModal = this.$el.closest(".modal");
            if($currentModal.length === 0 || $currentModal[0] !== $modal[0]) {
                click_outside = false;
            }
        }

        if (click_outside) {
            this._on_blur_one2many();
        }
    },
    _on_blur_one2many: function() {
        if(this.__ignore_blur) {
            return $.when();
        }

        this.__ignore_blur = true;
        this.__focus = false;
        this.dataset.x2m.internal_dataset_changed = false;

        var self = this;
        return this.save_edition(true).done(function () {
            var tmp = self.x2m.getParent().fields;
            self.x2m.getParent().fields.interns_clone.update_to_other();
            if (self._dataset_changed) {
                self.dataset.trigger('dataset_changed');
            }
        }).always(function() {
            self.__ignore_blur = false;
        });
    },
    _after_edit: function () {
        this.editor.form.on('blurred', this, this._on_blur_one2many);

        // The form's blur thing may be jiggered during the edition setup,
        // potentially leading to the x2m instasaving the row. Cancel any
        // blurring triggered the edition startup here
        this.editor.form.widgetFocused();
    },
    _before_unedit: function () {
        this.editor.form.off('blurred', this, this._on_blur_one2many);
    },
    do_delete: function (ids) {
        var confirm = window.confirm;
        window.confirm = function () { return true; };
        try {
            return this._super(ids);
        } finally {
            window.confirm = confirm;
        }
    },
    reload_record: function (record, options) {
        if (!options || !options.do_not_evict) {
            // Evict record.id from cache to ensure it will be reloaded correctly
            this.dataset.evict_record(record.get('id'));
        }

        return this._super(record);
    },



    data_create: function (data, options) {
        var self = this;
        if(this.dataset.child_name!='interns_clone'){
            return this.getParent().fields.interns_clone.send_commands([COMMANDS.create(data)], options).then(function(){
                return self.update_to_other();
            });
        }
        return this.send_commands([COMMANDS.create(data)], options).then(function(){
            self.update_to_other();
        });
    },

    /*
    *@value: id {int or string} id or virtual id of the record to update
    *        data {object} contains all value to send to the db
    *        options {object} options sent to the dataset
    *@return deferred
    */
    data_update: function (id, data, options) {
        var self = this;
        if(this.dataset.child_name!='interns_clone'){
            return this.getParent().fields.interns_clone.send_commands([COMMANDS.update(id, data)], options).then(function(){
                return self.update_to_other();
            });
        }
        return this.send_commands([COMMANDS.update(id, data)], options).then(function(){
            self.update_to_other();
        })
    },

    /*
    *@value: id {int or string} id or virtual id of the record to add
    *        options {object} options sent to the dataset
    *@return deferred
    */
    data_link: function (id, options) {
        return this.send_commands([COMMANDS.link_to(id)], options);
    },

    /*
    *@value: ids {array} list of ids or virtual ids of the record to add
    *        options {object} options sent to the dataset
    *@return deferred
    */
    data_link_multi: function (ids, options) {
        return this.send_commands(_.map(ids, function (id) { return COMMANDS.link_to(id); }), options);
    },

    /*
    *@value: id {int or string} id or virtual id of the record to unlink or delete (function of field type)
    *@return deferred
    */
    data_delete: function (id) {
        return this.send_commands([COMMANDS.delete(id)]);
    },

    /*
    *@value: id {int or string} id or virtual id of the record to removes relation (unlink or delete function of field type)
    *@return deferred
    */
    data_forget: function (id) {
        return this.send_commands([COMMANDS.forget(id)]);
    },

    /*
    *@value: ids {array} list of ids or virtual ids of the record who replace the previous list
    *        options {object} options sent to the dataset
    *@return deferred
    */
    data_replace: function (ids, options) {
        return this.send_commands([COMMANDS.replace_with(ids)], options);
    },

    /*
    *@value: ids {array} list of ids or virtual ids of the record to read
    *        fields {array} list of the field to read
    *        options {object} options sent to the dataset
    *@return deferred resolve with the records
    */
    data_read: function (ids, fields, options) {
        return this.dataset.read_ids(ids, fields, options);
    },


});

var FieldOne2ManyIntern = FieldOne2Many.extend({
    init: function() {
        this._super.apply(this, arguments);
        this.x2many_views = {
            list: One2ManyListViewNew,
            kanban: core.view_registry.get('one2many_kanban'),
        };
        if(this.name == 'interns_promoted'|| this.name=='interns_confirm_exam' || this.name=='interns_escape_exam'
            || this.name=='interns_pass_new'  || this.name=='interns_preparatory'  || this.name=='interns_cancel_pass'
            || this.name=='interns_departure'){
            this.dataset = this.getParent().fields.interns_clone.dataset;
        }
    },

    update_to_other: function(){
        var parent = this.getParent().fields;
        this.reload_current_view();
        if(parent.interns_promoted){
            parent.interns_promoted.reload_current_view();
        }
        return $.when();
    },

    //KIDO toggle button bool
    toggle_button_bool:function(id, field,options){
        var values = {};
        values[field] = !this.dataset.cache[id].values[field];
        if(options){
            var options_tmp = pyeval.py_eval(options);
            for (var t in options_tmp.related)
                values[options_tmp.related[t]] = false;
        }
        this.dataset.write(id,values,{});
        if(this.getParent().fields.interns_clone)
            this.getParent().fields.interns_clone.reload_current_view();
        if(this.getParent().fields.interns_promoted)
            this.getParent().fields.interns_promoted.reload_current_view();
        if(this.getParent().fields.interns_confirm_exam)
            this.getParent().fields.interns_confirm_exam.reload_current_view();
        if(this.getParent().fields.interns_escape_exam)
            this.getParent().fields.interns_escape_exam.reload_current_view();
        if(this.getParent().fields.interns_pass_new)
            this.getParent().fields.interns_pass_new.reload_current_view();
        if(this.getParent().fields.interns_preparatory)
            this.getParent().fields.interns_preparatory.reload_current_view();
        if(this.getParent().fields.interns_cancel_pass)
            this.getParent().fields.interns_cancel_pass.reload_current_view();
        if(this.getParent().fields.interns_departure)
            this.getParent().fields.interns_departure.reload_current_view();
    },

    toggle_delete_bool:function(id,field,options){

        var values = {};
        values[field] = false;
        if(options){
            var options_tmp = pyeval.py_eval(options);
            for (var t in options_tmp.related)
                values[options_tmp.related[t]] = false;
        }
        this.dataset.write(id,values,{});
        if(this.getParent().fields.interns_clone)
            this.getParent().fields.interns_clone.reload_current_view();
        if(this.getParent().fields.interns_promoted)
            this.getParent().fields.interns_promoted.reload_current_view();
        if(this.getParent().fields.interns_confirm_exam)
            this.getParent().fields.interns_confirm_exam.reload_current_view();
        if(this.getParent().fields.interns_escape_exam)
            this.getParent().fields.interns_escape_exam.reload_current_view();
        if(this.getParent().fields.interns_pass_new)
            this.getParent().fields.interns_pass_new.reload_current_view();
        if(this.getParent().fields.interns_preparatory)
            this.getParent().fields.interns_preparatory.reload_current_view();
        if(this.getParent().fields.interns_cancel_pass)
            this.getParent().fields.interns_cancel_pass.reload_current_view();
        if(this.getParent().fields.interns_departure)
            this.getParent().fields.interns_departure.reload_current_view();
    },

});

One2ManyListView.include({
    do_add_record: function () {
//        if (this.editable()) {
//            this._super.apply(this, arguments);
//        }
        if (!('showslection' in this.fields_view.arch.attrs)){
            this._super.apply(this, arguments);
        }else{
            var self = this;
            new common.SelectCreateDialog(this, {
                res_model: this.model,
                domain: new data.CompoundDomain(this.x2m.build_domain(), ["!", ["id", "in", this.x2m.dataset.ids]]),
                context: this.x2m.build_context(),
                title: _t("Add: ") + this.x2m.string,
                alternative_form_view: this.x2m.field.views ? this.x2m.field.views.form : undefined,
                no_create: this.x2m.options.no_create || !this.is_action_enabled('create'),
                on_selected: function(element_ids) {

                    return self.x2m.data_link_multi(element_ids).then(function() {
                        if ('sequence_pass' in self.fields_view.fields){
                            var smallest = 1;
                            _.each(self.x2m.dataset.ids, function(id){
                                self.x2m.dataset.read_ids([id],['sequence_pass'],{}).then(function (records) {
                                    if(records[0].sequence_pass>smallest){
                                        smallest = records[0].sequence_pass;
                                    }
                                });
                            });
                            _.each(element_ids, function (id) {
                                    smallest = smallest+1;
                                    self.x2m.dataset._update_cache(id,{'changes':{'sequence_pass':smallest}});
                                }
                            );
                        }
                        else if ('sequence' in self.fields_view.fields){
                            var smallest = 1;
                            _.each(self.x2m.dataset.ids, function(id){
                                self.x2m.dataset.read_ids([id],['sequence'],{}).then(function (records) {
                                    if(records[0].sequence_pass>smallest){
                                        smallest = records[0].sequence_pass;
                                    }
                                });
                            });
                            _.each(element_ids, function (id) {
                                    smallest = smallest+1;
                                    self.x2m.dataset._update_cache(id,{'changes':{'sequence':smallest}});
                                }
                            );
                        }
                        self.x2m.reload_current_view();
                    });
                }
            }).open();
        }
    },
    data_link_multi: function (ids, options) {
        return this.send_commands(_.map(ids, function (id) { return COMMANDS.link_to(id); }), options);
    },



});

FieldOne2Many.include({
    get_value: function() {
        var self = this,
            is_one2many = this.field.type === "one2many",
            not_delete = this.options.not_delete,
            starting_ids = this.starting_ids.slice(),
            replace_with_ids = [],
            add_ids = [],
            command_list = [],
            id, index, record;

        _.each(this.get('value'), function (id) {
            index = starting_ids.indexOf(id);
            if (index !== -1) {
                starting_ids.splice(index, 1);
            }
            var record = self.dataset.get_cache(id);
            if (!_.isEmpty(record.changes)) {
                var values = _.clone(record.changes);
                // format many2one values
                for (var k in values) {
                    if ((values[k] instanceof Array) && values[k].length === 2 && typeof values[k][0] === "number" && typeof values[k][1] === "string") {
                        values[k] = values[k][0];
                    }
                }
                if (record.to_create) {
                    command_list.push(COMMANDS.create(values));
                } else {
                    command_list.push(COMMANDS.update(record.id, values));
                }
                return;
            }
            if (!is_one2many || not_delete || self.dataset.delete_all) {
                replace_with_ids.push(id);
            } else {
                command_list.push(COMMANDS.link_to(id));
            }
        });
        if ((!is_one2many || not_delete || self.dataset.delete_all) && (replace_with_ids.length || starting_ids.length)
            || (is_one2many && 'views' in self && typeof self.views[0].fields_view != 'undefined' && 'showslection' in self.views[0].fields_view.arch.attrs)) {
            _.each(command_list, function (command) {
                if (command[0] === COMMANDS.UPDATE) {
                    replace_with_ids.push(command[1]);
                }
            });
            command_list.unshift(COMMANDS.replace_with(replace_with_ids));
        }

        _.each(starting_ids, function(id) {
            if (is_one2many && !not_delete) {
                command_list.push(COMMANDS.delete(id));
            } else if (is_one2many && !self.dataset.delete_all) {
                command_list.push(COMMANDS.forget(id));
            }
        });

        return command_list;
    },

})


//var One2ManyListViewAutoSave = One2ManyListView.extend({
//    do_activate_record: function(index, id) {
//        var self = this;
//        var pop = new common.FormViewDialog(self, {
//            res_model: self.x2m.field.relation,
//            res_id: id,
//            context: self.x2m.build_context(),
//            title: _t("Open: ") + self.x2m.string,
////            write_function: function(id, data, options) {
////                return self.x2m.data_update(id, data, options).done(function() {
////                    self.x2m.reload_current_view();
////                });
////            },
//            write_function = function(id, data, options, sup) {
//                var fct = self.options.write_function || sup;
//                return fct.call(this, id, data, options).done(function(r) {
////                    self.trigger('write_completed saved', r);
////                    self.x2m.data_update(id, data, options)
////                    self.x2m.reload_current_view();
//                    return self.x2m.data_update(id, data, options).done(function() {
//                        self.x2m.reload_current_view();
//                    });
//                });
//            },
//            alternative_form_view: self.x2m.field.views ? self.x2m.field.views.form : undefined,
//            parent_view: self.x2m.view,
//            child_name: self.x2m.name,
//            read_function: function(ids, fields, options) {
//                return self.x2m.data_read(ids, fields, options);
//            },
//            form_view_options: {'not_interactible_on_create':true},
//            readonly: !this.is_action_enabled('edit') || self.x2m.get("effective_readonly")
//        }).open();
//
////        pop.on('write_completed', self, function () {
////            self.dataset.evict_record(id);
////            self.reload_content();
//////            self.x2m.reload_current_view();
////        });
//    },
//
//});
//
//var FieldOne2ManyAutoSaved = FieldOne2Many.extend({
//    init: function() {
//        this._super.apply(this, arguments);
//        this.x2many_views = {
//            kanban: core.view_registry.get('one2many_kanban'),
//            list: One2ManyListViewAutoSave,
//        };
//    },
//});

core.form_widget_registry.add('many2many_intern', FieldMany2ManyIntern);
core.form_widget_registry.add('one2many_intern', FieldOne2ManyIntern);
//core.form_widget_registry.add('one2many_saved', FieldOne2ManyAutoSaved);


});
