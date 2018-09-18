odoo.define('hh_intern.data', function (require) {
"use strict";
var core = require('web.core');
var list_widget_registry = core.list_widget_registry;

//var DataSet =  Class.extend(mixins.PropertiesMixin, {
//
//    init: function(parent, model, context) {
//        this._super(parent, model, context);
//    },
//    add_ids: function(ids, at) {
//        alert("ID111 " + this.ids + " " + at)
//        //var args = [at, 0].concat(_.difference(ids, this.ids));
//        var args = [this.ids.length,0].concat(_.difference(ids, this.ids));
//        alert("ID2333 " + args)
//        this.ids.splice.apply(this.ids, args);
//
//        alert("ID222 " + this.ids)
//    },
//});


var Column = list_widget_registry.get('field').extend({
    width: function () {
        var self = this;
        if ('style' in this){
            return this['style'];
        }
        return 3;
    },
});

//var ColumnChar = list_widget_registry.get('field.char').extend({
//    width: function () {
//        var self = this;
//        if ('style' in this){
//            return this['style'];
//        }
//    },
//});
//
//list_widget_registry.add('field', Column).add('field.char', ColumnChar);

});