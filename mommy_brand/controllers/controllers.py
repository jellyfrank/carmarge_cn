# -*- coding: utf-8 -*-
# from odoo import http


# class MommyBrand(http.Controller):
#     @http.route('/mommy_brand/mommy_brand/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mommy_brand/mommy_brand/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mommy_brand.listing', {
#             'root': '/mommy_brand/mommy_brand',
#             'objects': http.request.env['mommy_brand.mommy_brand'].search([]),
#         })

#     @http.route('/mommy_brand/mommy_brand/objects/<model("mommy_brand.mommy_brand"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mommy_brand.object', {
#             'object': obj
#         })
