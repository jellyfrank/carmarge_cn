# -*- coding: utf-8 -*-
# from odoo import http


# class CarmargeStockCn(http.Controller):
#     @http.route('/carmarge_stock_cn/carmarge_stock_cn/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/carmarge_stock_cn/carmarge_stock_cn/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('carmarge_stock_cn.listing', {
#             'root': '/carmarge_stock_cn/carmarge_stock_cn',
#             'objects': http.request.env['carmarge_stock_cn.carmarge_stock_cn'].search([]),
#         })

#     @http.route('/carmarge_stock_cn/carmarge_stock_cn/objects/<model("carmarge_stock_cn.carmarge_stock_cn"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('carmarge_stock_cn.object', {
#             'object': obj
#         })
