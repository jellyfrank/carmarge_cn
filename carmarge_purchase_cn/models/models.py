#!/usr/bin/python3
# @Time    : 2022-01-25
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class purchase_order(models.Model):

    _inherit = "purchase.order"

    @api.depends('order_line.price_total', "delivery_cost", "discount_manual")
    def _amount_all(self):
        super(purchase_order, self)._amount_all()
        # 添加运费和优惠
        for order in self:
            order.update({
                "amount_total": order.amount_total + order.delivery_cost - order.discount_manual
            })

    delivery_cost = fields.Monetary("运费")
    discount_manual = fields.Monetary("优惠")


class purchase_order_line(models.Model):

    _inherit = "purchase.order.line"

    @api.depends("order_id.delivery_cost", "order_id.discount_manual")
    def _compute_line(self):
        for line in self:
            line.delivery_cost_line = line.order_id.delivery_cost / len(line.order_id.order_line)
            line.discount_manual_line = line.order_id.discount_manual / len(line.order_id.order_line)

    delivery_cost_line = fields.Monetary(
        "运费", compute="_compute_line", store=True)
    discount_manual_line = fields.Monetary(
        "优惠", compute="_compute_line", store=True)
