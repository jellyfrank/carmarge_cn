# -*- coding: utf-8 -*-
# from odoo import http


# class CarmargeSaleCn(http.Controller):
#     @http.route('/carmarge_sale_cn/carmarge_sale_cn/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/carmarge_sale_cn/carmarge_sale_cn/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('carmarge_sale_cn.listing', {
#             'root': '/carmarge_sale_cn/carmarge_sale_cn',
#             'objects': http.request.env['carmarge_sale_cn.carmarge_sale_cn'].search([]),
#         })

#     @http.route('/carmarge_sale_cn/carmarge_sale_cn/objects/<model("carmarge_sale_cn.carmarge_sale_cn"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('carmarge_sale_cn.object', {
#             'object': obj
#         })
