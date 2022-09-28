#!/usr/bin/python3
# @Time    : 2022-09-28
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _
from odoo.exceptions import UserError



class ir_actions_report(models.Model):
    _inherit = "ir.actions.report"
    
    FUNC_METHOD = '_validate_report'


    def _render_template(self, template, values=None):
        doc_model_obj = self.env[values['doc_model']]
        if hasattr(doc_model_obj, self.FUNC_METHOD):
            records = values['docs']
            getattr(records, self.FUNC_METHOD)()
        return super()._render_template(template, values)
