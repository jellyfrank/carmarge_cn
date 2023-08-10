#!/usr/bin/python3
# @Time    : 2022-03-30
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BaseModel(models.AbstractModel):

    _inherit = "base"

    def _compute_action_show_nickname(self):
        self.action_show_nickname = False

    @api.model
    def _add_magic_fields(self):
        """Add field action show nickname or not."""
        field = fields.Boolean("Action show nickname?",
                               compute="_compute_action_show_nickname")
        self._add_field('action_show_nickname', field)
        return super()._add_magic_fields()

    def _pre_report_action(self):
        pass

    def _pre_action_validate(self):
        pass

    @api.model
    def _create(self, data_list):
        for data in data_list:
            # determine column values
            stored = data['stored']
            for name, val in sorted(stored.items()):
                field = self._fields[name]
                if field.type == 'char' and field.unique:
                    record = self.search([(name, '=', val)], limit=1)
                    if record:
                        msg = _("This field was restricted to unique, value %s already existed!") %val if not field.exception else field.exception
                        raise UserError(msg)
        return super()._create(data_list)

    def _write(self, vals):
        for name, val in sorted(vals.items()):
            field = self._fields[name]
            if field.type == 'char' and field.unique:
                record = self.search([(name, '=', val)], limit=1)
                if record:
                    msg = _("This field was restricted to unique, value %s already existed!") %val if not field.exception else field.exception
                    raise UserError(msg)
        return super()._write(vals)

    @property
    def active_model(self):
        return self._context.get("active_model")

    @property
    def active_records(self):
        active_model, active_id, active_ids = self._context.get(
            "active_model"), self._context.get("active_id"), self._context.get("active_ids")
        if not active_model:
            return None
        if active_ids:
            return self.env[active_model].browse(active_ids)
        if active_id:
            return self.env[active_model].browse(active_id)

    @api.model
    def next_by_code(self):
        return self.env['ir.sequence'].sudo().next_by_code(self._name)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(BaseModel, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        
        
        for field_name in fields:
            _field = field_name.split(':')[0]
            if _field not in self._fields:
                continue
            field = self._fields[_field]
            if (field.compute or field.related) and hasattr(field, 'group') and getattr(field, 'group'):
                if field.type in ('integer', 'float', 'moneytary'):
                    # need it add sum
                    for group in res:
                        if '__domain' in group:
                            records = self.search(group['__domain'])
                            # [FIXME] only sum today.
                            group[field_name] = sum(
                                getattr(record, field_name) for record in records)
                # if field.type == 'many2one':
                #     for group in res:
                #         if '__domain' in group:
                #             records = self.search(group['__domain'])
                #             # [FIXME] only sum today.
                #             group[field_name] = getattr(records[0], field_name)
        return res

    def show_message(self, title, content):
        popsup = self.env['mommy.message.popsup'].create({
            "name": title,
            "content": content
        })
        return popsup.get_action()

    def show_confirm_message(self, title, content):
        confirm_pops_up = self.env['mommy.message.popsup'].create({
            "name": title,
            "content": content
        })
        return confirm_pops_up.get_confirm_action()


    def get_selection_desc(self, field):
        if self._fields[field].type != 'selection':
            raise UserError(_("Only selection fields can use this method."))
        return dict(self._fields[field]._description_selection(self.env)).get(getattr(self, field))

    def get_view_action(self, action_id=None, view_id=None, view_mode=None):
        """get view action"""
        model, res_ids = self._name, self.ids

        if not action_id:
            domain = [('res_model', '=', model)]
            action_id = self.env['ir.actions.act_window'].search(
                domain, limit=1)
        if not action_id:
            raise UserError(
                _("Model: %s has no valid action for this operation." % model))

        if not view_mode:
            if len(res_ids) == 1:
                mode = 'form'
            else:
                mode = 'tree'
        else:
            mode = view_mode

        if not view_id:
            domain = [('model', '=', model), ('type', '=', mode)]
            view_id = self.env['ir.ui.view'].search(domain, limit=1)
        else:
            view_id = self.env.ref(view_id).id

        action = action_id.read()[0]
        if mode == 'form':
            action['res_id'] = res_ids[0]
            action['views'] = [(view_id.id, mode)]
        else:
            if not action['view_mode'].startswith('tree'):
                action['view_mode'] = 'tree'
            if action['views']:
                action.pop('views')
            action['domain'] = [('id', 'in', res_ids)]
        return action
