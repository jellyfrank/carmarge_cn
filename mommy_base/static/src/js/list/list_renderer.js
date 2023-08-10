odoo.define("mommy_base.list_renderder", function (require) {
    'use strict';

    var ListRenderder = require("web.ListRenderer");
    var config = require('web.config');
    var field_utils = require('web.field_utils');

    var FIELD_CLASSES = {
        char: 'o_list_char',
        float: 'o_list_number',
        integer: 'o_list_number',
        monetary: 'o_list_number',
        text: 'o_list_text',
        many2one: 'o_list_many2one',
    };

    ListRenderder.include({
        _renderHeaderCell: function (node) {
            const { icon, name, string } = node.attrs;
            var order = this.state.orderedBy;
            var isNodeSorted = order[0] && order[0].name === name;
            var field = this.state.fields[name];
            var $th = $('<th>');
            if (name) {
                $th.attr('data-name', name);
            } else if (string) {
                $th.attr('data-string', string);
            } else if (icon) {
                $th.attr('data-icon', icon);
            }
            if (node.attrs.editOnly) {
                $th.addClass('oe_edit_only');
            }
            if (node.attrs.readOnly) {
                $th.addClass('oe_read_only');
            }
            if (node.tag === 'button_group') {
                $th.addClass('o_list_button');
            }
            if (!field || node.attrs.nolabel === '1') {
                return $th;
            }
            var description = string || field.string;
            if (node.attrs.widget) {
                $th.addClass(' o_' + node.attrs.widget + '_cell');
                const FieldWidget = this.state.fieldsInfo.list[name].Widget;
                if (FieldWidget.prototype.noLabel) {
                    description = '';
                } else if (FieldWidget.prototype.label) {
                    description = FieldWidget.prototype.label;
                }
            }
            $th.text(description)
                .attr('tabindex', -1)
                .toggleClass('o-sort-down', isNodeSorted ? !order[0].asc : false)
                .toggleClass('o-sort-up', isNodeSorted ? order[0].asc : false)
                .addClass((field.sortable || this.state.fieldsInfo.list[name].options.allow_order || false) && 'o_column_sortable');

            if (isNodeSorted) {
                $th.attr('aria-sort', order[0].asc ? 'ascending' : 'descending');
            }

            if (field.type === 'float' || field.type === 'integer' || field.type === 'monetary') {
                $th.addClass('o_list_number_th');
            }

            if (config.isDebug()) {
                var fieldDescr = {
                    field: field,
                    name: name,
                    string: description || name,
                    record: this.state,
                    attrs: _.extend({}, node.attrs, this.state.fieldsInfo.list[name]),
                };
                this._addFieldTooltip(fieldDescr, $th);
            } else {
                $th.attr('title', description);
            }

            if ($th[0].innerHTML.length && this._hasVisibleRecords(this.state)) {
                const resizeHandle = document.createElement('span');
                resizeHandle.classList = 'o_resize';
                resizeHandle.onclick = this._onClickResize.bind(this);
                resizeHandle.onmousedown = this._onStartResize.bind(this);
                $th.append(resizeHandle);
            }
            
            return $th;
        },

        _renderBodyCell: function (record, node, colIndex, options) {
            var tdClassName = 'o_data_cell';
            if (node.tag === 'button_group') {
                tdClassName += ' o_list_button';
            } else if (node.tag === 'field') {
                tdClassName += ' o_field_cell';
                var typeClass = FIELD_CLASSES[this.state.fields[node.attrs.name].type];
                if (typeClass) {
                    tdClassName += (' ' + typeClass);
                }
                if (node.attrs.widget) {
                    tdClassName += (' o_' + node.attrs.widget + '_cell');
                }
            }
            if (node.attrs.editOnly) {
                tdClassName += ' oe_edit_only';
            }
            if (node.attrs.readOnly) {
                tdClassName += ' oe_read_only';
            }
            if (node.attrs.class) {
                tdClassName += (' ' + node.attrs.class)
            }
            var $td = $('<td>', { class: tdClassName, tabindex: -1 });

            // We register modifiers on the <td> element so that it gets the correct
            // modifiers classes (for styling)
            var modifiers = this._registerModifiers(node, record, $td, _.pick(options, 'mode'));
            // If the invisible modifiers is true, the <td> element is left empty.
            // Indeed, if the modifiers was to change the whole cell would be
            // rerendered anyway.
            if (modifiers.invisible && !(options && options.renderInvisible)) {
                return $td;
            }

            if (node.tag === 'button_group') {
                for (const buttonNode of node.children) {
                    if (!this.columnInvisibleFields[buttonNode.attrs.name]) {
                        $td.append(this._renderButton(record, buttonNode));
                    }
                }
                return $td;
            } else if (node.tag === 'widget') {
                return $td.append(this._renderWidget(record, node));
            }
            if (node.attrs.widget || (options && options.renderWidgets)) {
                var $el = this._renderFieldWidget(node, record, _.pick(options, 'mode'));
                return $td.append($el);
            }
            this._handleAttributes($td, node);
            this._setDecorationClasses($td, this.fieldDecorations[node.attrs.name], record);

            var name = node.attrs.name;
            var field = this.state.fields[name];
            var value = record.data[name];
            var formatter = field_utils.format[field.type];
            var formatOptions = {
                escape: true,
                data: record.data,
                isPassword: 'password' in node.attrs,
                digits: node.attrs.digits && JSON.parse(node.attrs.digits),
            };
            var formattedValue = formatter(value, field, formatOptions);
            var title = '';
            if (field.type !== 'boolean') {
                title = formatter(value, field, _.extend(formatOptions, { escape: false }));
            }
            return $td.html(formattedValue).attr('title', title);
        }
    });
});