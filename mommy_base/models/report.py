#!/usr/bin/python3
# @Time    : 2022-10-31
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _
from odoo.tools import config, is_html_empty, parse_version


class ir_actions_report(models.Model):
    _inherit="ir.actions.report"

    def _get_rendering_context(self, docids, data):
        # If the report is using a custom model to render its html, we must use it.
        # Otherwise, fallback on the generic html rendering.
        report_model = self._get_rendering_context_model()

        data = data and dict(data) or {}

        if report_model is not None:
            # _render_ may be executed in sudo but evaluation context as real user
            report_model = report_model.sudo(False)
            data.update(report_model._get_report_values(docids, data=data))
        else:
            # _render_ may be executed in sudo but evaluation context as real user
            docs = self.env[self.model].sudo(False).browse(docids)
            data.update({
                'doc_ids': docids,
                'doc_model': self.model,
                'docs': docs,
            })
            # check action before renderring
            docs._pre_report_action()
        data['is_html_empty'] = is_html_empty
        return data

    nickname = fields.Char("Nick Name")