#!/usr/bin/python3
# @Time    : 2022-01-25
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class sale_order(models.Model):

    _inherit = "sale.order"

    @api.depends('order_line.price_total', "delivery_cost", "discount_manual")
    def _amount_all(self):
        super(sale_order, self)._amount_all()
        # 添加运费和优惠
        for order in self:
            order.update({
                "amount_total": order.amount_total + order.delivery_cost - order.discount_manual
            })

    delivery_cost = fields.Monetary("运费")
    discount_manual = fields.Monetary("优惠")
