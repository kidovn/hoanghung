odoo.define('hh_override.DataExport', function (require) {
"use strict";
    var DataExport = require('web.DataExport');
    DataExport.extend({
        template: 'TestExportDialog',
        init: function(parent, dataset) {
            this._super.apply(this, arguments);
            this.template = 'TestExportDialog';
        },
    });
});