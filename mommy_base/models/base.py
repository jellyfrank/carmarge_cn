#!/usr/bin/python3
# @Time    : 2022-03-30
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class BaseModel(models.AbstractModel):

    _inherit="base"

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(BaseModel,self).read_group(
            domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for field_name in fields:
            field = self._fields[field_name.split(':')[0]]
            if field.compute and hasattr(field, 'group') and getattr(field, 'group') and field.type in ('integer','float','moneytary'):
                # need it add sum
                for group in res:
                    if '__domain' in group:
                        records = self.search(group['__domain'])
                        # [FIXME] only sum today.
                        group[field_name] = sum(getattr(record, field_name) for record in records)
        return res

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