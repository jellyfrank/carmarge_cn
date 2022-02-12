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
            line.delivery_cost_line = line.order_id.delivery_cost / \
                len(line.order_id.order_line)
            line.discount_manual_line = line.order_id.discount_manual / \
                len(line.order_id.order_line)

    @api.depends("product_id")
    def _get_product_packaging(self):
        """获取包裹数量"""
        # 取产品库存包装信息中的第一条
        for line in self:
            line.packaging = line.product_id.packaging_ids[0] if line.product_id.packaging_ids else None

    @api.depends("packaging","product_qty")
    def _compute_packaging_qty(self):
        """计算包裹数量"""
        for line in self:
            line.packaging_qty = line.product_qty / \
                line.packaging.qty if line.packaging.qty != 0 else 0

    @api.depends("packaging","product_qty")
    def _compute_total(self):
        for line in self:
            line.total_packaging_weight = line.packaging_qty * line.packaging.weight
            line.total_packaging_volume = line.packaging_qty * line.packaging.volume
            line.total_packaging_net_weight = line.packaging_qty * line.packaging_net_weight

    delivery_cost_line = fields.Monetary(
        "运费", compute="_compute_line", store=True)
    discount_manual_line = fields.Monetary(
        "优惠", compute="_compute_line", store=True)
    packaging = fields.Many2one(
        "product.packaging", string="包裹", compute="_get_product_packaging")
    packaging_qty = fields.Float(
        "包裹数", compute="_compute_packaging_qty", store=True)
    packaging_weight = fields.Float(
        "包装毛重", related="packaging.weight", store=True)
    packaging_net_weight = fields.Float(
        "包装净重", related="packaging.net_weight", store=True)
    packaging_volume = fields.Float(
        "包装体积", related="packaging.volume", store=True)
    total_packaging_weight = fields.Float("总包装毛重", compute="_compute_total")
    total_packaging_net_weight = fields.Float("总包装毛重", compute="_compute_total")
    total_packaging_volume = fields.Float("总包装毛重", compute="_compute_total")
    weight = fields.Float("毛重", related="product_id.weight")
    net_weight = fields.Float("净重", related="product_id.net_weight")
    volume = fields.Float("体积", related="product_id.volume")
