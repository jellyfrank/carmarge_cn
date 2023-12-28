#!/usr/bin/python3
# @Time    : 2022-11-01
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Action


class ActionController(Action):

    @http.route('/web/action/load', type='json', auth="user")
    def load(self, action_id, additional_context=None):
        if additional_context and additional_context.get('active_model') and additional_context.get("active_ids"):
            active_model, active_id, active_ids = additional_context[
                'active_model'], additional_context['active_id'], additional_context['active_ids']
            active_records = request.env[active_model].browse(active_id) if active_id else request.env[active_model].browse(active_ids)
            active_records._pre_action_validate()
        return super().load(action_id, additional_context)

    @http.route('/web/attachment/<int:id>', type='http', auth="public")
    def download_attachments(self, file_name, id):
        """
        Download file bytes
        """
        attach = request.env['ir.attchment'].sudo().browse(id)
        headers = [('Content-Type', 'application/ms-excel'),
                   ('Content-Disposition', content_disposition(file_name))]
        return request.make_response(attach.raw,
                                     headers=headers)
