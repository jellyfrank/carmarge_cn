#!/usr/bin/python3
# @Time    : 2022-02-13
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class account_move(models.Model):

    _inherit = "account.move"

    
    amount_total = fields.Monetary(string='Total', store=True, readonly=True,
        compute='_compute_amount',
        inverse='_inverse_amount_total')

    # @api.model
    # def default_get(self,fields):
    #     """获取默认值"""
    #     res = super(account_move,self).default_get(fields)
    #     if self.env.context.get("active_model") == "sale.order":
    #         sale_order = self.env['sale.order'].sudo().browse(self.env.context.get("active_id"))
    #         res['delivery_cost'] = sale_order.delivery_cost
    #         res['discount_manual'] = sale_order.discount_manual
    #     return res