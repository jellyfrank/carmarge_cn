odoo.define("mommy_base.form", function (require) {
    'use strict';
    
    var FormView = require("web.FormView");

    FormView.include({
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
            if (params.activeActions) {
                this.controllerParams.activeActions = params.activeActions;
            }
        }
    });
    
});