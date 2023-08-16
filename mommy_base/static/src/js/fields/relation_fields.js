odoo.define("mommy_base.x2m_no_open", function (require) {
    'use strict';

    //继承自web view_dialog
    // var ViewDialog = require("web.view_dialogs");
    var RelationFields = require("web.relational_fields");
    // var view_registry = require('web.view_registry');
    // var dom = require('web.dom');

    var One2manyField = RelationFields.FieldOne2Many;
    var Many2manyField = RelationFields.FieldMany2Many;

    One2manyField.include({

        _onOpenRecord: function (ev) {
            if (this.nodeOptions && this.nodeOptions.no_open) {
                ev.stopPropagation();
                return
            }
            this._super.apply(this,arguments);
        },
    });

    Many2manyField.include({

        _onOpenRecord: function (ev) {

            if (this.nodeOptions && this.nodeOptions.no_open) {
                ev.stopPropagation();
                return
            }
            this._super.apply(this,arguments);
        },
    });


});