# -*- coding: utf-8 -*-
# from odoo import http


# class CarmargePartnerCn(http.Controller):
#     @http.route('/carmarge_partner_cn/carmarge_partner_cn/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/carmarge_partner_cn/carmarge_partner_cn/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('carmarge_partner_cn.listing', {
#             'root': '/carmarge_partner_cn/carmarge_partner_cn',
#             'objects': http.request.env['carmarge_partner_cn.carmarge_partner_cn'].search([]),
#         })

#     @http.route('/carmarge_partner_cn/carmarge_partner_cn/objects/<model("carmarge_partner_cn.carmarge_partner_cn"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('carmarge_partner_cn.object', {
#             'object': obj
#         })
