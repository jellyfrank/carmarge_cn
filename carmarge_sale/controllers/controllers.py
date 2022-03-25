# -*- coding: utf-8 -*-
# from odoo import http


# class CarmergeSale(http.Controller):
#     @http.route('/carmerge_sale/carmerge_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/carmerge_sale/carmerge_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('carmerge_sale.listing', {
#             'root': '/carmerge_sale/carmerge_sale',
#             'objects': http.request.env['carmerge_sale.carmerge_sale'].search([]),
#         })

#     @http.route('/carmerge_sale/carmerge_sale/objects/<model("carmerge_sale.carmerge_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('carmerge_sale.object', {
#             'object': obj
#         })
