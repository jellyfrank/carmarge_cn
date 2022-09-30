odoo.define("list_preview.ListPreview", function (require) {
    'use strict';

    var core = require("web.core");
    var QWeb = core.qweb;

    var Widget = require("web.Widget");
    var _t = core._t;
    // var widget_registry = require("web.widget_registry");
    var field_registry = require("web.field_registry");
    var config = require("web.config");
    var AbstractField = require("web.AbstractField");

    var ListPreview = AbstractField.extend({
        noLabel: true,
        template: 'list_preview_widget.Preview',
        fieldDependencies: _.extend({}, AbstractField.prototype.fieldDependencies, {
            activity_exception_icon: { type: 'char' }
        }),
        events: _.extend({}, Widget.prototype.events, {}),

        start: function () {
            var self = this;
            self.$('.' + self.record.data.activity_exception_icon).on('click',self._onClickButton);
            return self._super.apply(this, arguments).then(function () {
                self._setPopOver();
            })
        },

        _setPopOver: function () {
            var self = this;
            var $content = $(QWeb.render('list_preview_widget.PreviewPopup', {
                data: self.value
            }));
            var options = {
                container: 'body',
                content: $content,
                html: true,
                placement: 'left',
                title: _t(self.field.string),
                trigger: 'focus',
                delay: { 'show': 0, 'hide': 100 },
            };
            this.$el.popover(options);
        },

        _onClickButton: function () {
            $(this).prop('special_click', true);
        }
    });

    field_registry.add("list_preview", ListPreview);

    return ListPreview;
});