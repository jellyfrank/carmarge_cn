# -*- coding: utf-8 -*-
# from odoo import http


# class ProductHistory(http.Controller):
#     @http.route('/product_history/product_history/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_history/product_history/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_history.listing', {
#             'root': '/product_history/product_history',
#             'objects': http.request.env['product_history.product_history'].search([]),
#         })

#     @http.route('/product_history/product_history/objects/<model("product_history.product_history"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_history.object', {
#             'object': obj
#         })
