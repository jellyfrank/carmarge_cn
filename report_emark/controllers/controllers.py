# -*- coding: utf-8 -*-
# from odoo import http


# class ReportEmark(http.Controller):
#     @http.route('/report_emark/report_emark/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_emark/report_emark/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_emark.listing', {
#             'root': '/report_emark/report_emark',
#             'objects': http.request.env['report_emark.report_emark'].search([]),
#         })

#     @http.route('/report_emark/report_emark/objects/<model("report_emark.report_emark"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_emark.object', {
#             'object': obj
#         })
