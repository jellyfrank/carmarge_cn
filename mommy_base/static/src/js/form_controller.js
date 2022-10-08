odoo.define("mommy_base.FormController", function (require) {
    'use strict';
    
    var FormController = require("web.FormController");

    FormController.include({
        _getActionMenuItems: function (state) {
            $.each(this.toolbarActions.print,function(index,print){
                if(state.data.action_show_nickname && print.nickname){
                    print.name = print.nickname
                }
            })
            return this._super(...arguments);
        }
    });
});