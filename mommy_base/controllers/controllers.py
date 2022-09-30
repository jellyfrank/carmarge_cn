# -*- coding: utf-8 -*-
# from odoo import http


# class MommyCore(http.Controller):
#     @http.route('/mommy_core/mommy_core/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mommy_core/mommy_core/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mommy_core.listing', {
#             'root': '/mommy_core/mommy_core',
#             'objects': http.request.env['mommy_core.mommy_core'].search([]),
#         })

#     @http.route('/mommy_core/mommy_core/objects/<model("mommy_core.mommy_core"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mommy_core.object', {
#             'object': obj
#         })
