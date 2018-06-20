odoo.define('web.data', function (require) {
"use strict";


var DataSet =  Class.extend(mixins.PropertiesMixin, {

    init: function(parent, model, context) {
        this._super(parent, model, context);
    },
    add_ids: function(ids, at) {
        alert("ID111 " + this.ids + " " + at)
        //var args = [at, 0].concat(_.difference(ids, this.ids));
        var args = [this.ids.length,0].concat(_.difference(ids, this.ids));
        alert("ID2333 " + args)
        this.ids.splice.apply(this.ids, args);

        alert("ID222 " + this.ids)
    },
});

