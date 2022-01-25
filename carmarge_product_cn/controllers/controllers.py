# -*- coding: utf-8 -*-
# from odoo import http


# class CarmargeProductCn(http.Controller):
#     @http.route('/carmarge_product_cn/carmarge_product_cn/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/carmarge_product_cn/carmarge_product_cn/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('carmarge_product_cn.listing', {
#             'root': '/carmarge_product_cn/carmarge_product_cn',
#             'objects': http.request.env['carmarge_product_cn.carmarge_product_cn'].search([]),
#         })

#     @http.route('/carmarge_product_cn/carmarge_product_cn/objects/<model("carmarge_product_cn.carmarge_product_cn"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('carmarge_product_cn.object', {
#             'object': obj
#         })
