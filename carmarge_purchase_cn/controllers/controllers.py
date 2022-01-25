# -*- coding: utf-8 -*-
# from odoo import http


# class CarmargePurchaseCn(http.Controller):
#     @http.route('/carmarge_purchase_cn/carmarge_purchase_cn/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/carmarge_purchase_cn/carmarge_purchase_cn/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('carmarge_purchase_cn.listing', {
#             'root': '/carmarge_purchase_cn/carmarge_purchase_cn',
#             'objects': http.request.env['carmarge_purchase_cn.carmarge_purchase_cn'].search([]),
#         })

#     @http.route('/carmarge_purchase_cn/carmarge_purchase_cn/objects/<model("carmarge_purchase_cn.carmarge_purchase_cn"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('carmarge_purchase_cn.object', {
#             'object': obj
#         })
