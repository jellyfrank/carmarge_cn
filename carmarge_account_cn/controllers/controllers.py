# -*- coding: utf-8 -*-
# from odoo import http


# class CarmargeAccountCn(http.Controller):
#     @http.route('/carmarge_account_cn/carmarge_account_cn/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/carmarge_account_cn/carmarge_account_cn/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('carmarge_account_cn.listing', {
#             'root': '/carmarge_account_cn/carmarge_account_cn',
#             'objects': http.request.env['carmarge_account_cn.carmarge_account_cn'].search([]),
#         })

#     @http.route('/carmarge_account_cn/carmarge_account_cn/objects/<model("carmarge_account_cn.carmarge_account_cn"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('carmarge_account_cn.object', {
#             'object': obj
#         })
