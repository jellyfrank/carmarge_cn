# -*- coding: utf-8 -*-
# from odoo import http


# class ListPreviewWidget(http.Controller):
#     @http.route('/list_preview_widget/list_preview_widget/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/list_preview_widget/list_preview_widget/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('list_preview_widget.listing', {
#             'root': '/list_preview_widget/list_preview_widget',
#             'objects': http.request.env['list_preview_widget.list_preview_widget'].search([]),
#         })

#     @http.route('/list_preview_widget/list_preview_widget/objects/<model("list_preview_widget.list_preview_widget"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('list_preview_widget.object', {
#             'object': obj
#         })
