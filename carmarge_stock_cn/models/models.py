#!/usr/bin/python3
# @Time    : 2022-03-08
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class stock_move(models.Model):
    _inherit = "stock.move"

    @api.depends("product_id")
    def _get_product_packaging(self):
        """获取包裹数量"""
        # 取产品库存包装信息中的第一条
        for move in self:
            move.packaging = move.product_id.packaging_ids[0] if move.product_id.packaging_ids else None

    @api.depends("packaging", "product_qty")
    def _compute_packaging_qty(self):
        """计算包裹数量"""
        for line in self:
            line.packaging_qty = line.product_qty / \
                line.packaging.qty if line.packaging.qty != 0 else 0

    @api.depends("packaging", "product_qty")
    def _compute_total(self):
        for line in self:
            line.total_packaging_weight = line.packaging_qty * line.packaging.weight
            line.total_packaging_volume = line.packaging_qty * line.packaging.volume
            line.total_packaging_net_weight = line.packaging_qty * line.packaging_net_weight

    packaging = fields.Many2one("product.packaging",string="包装规格", compute="_get_product_packaging")
    packaging_qty = fields.Float(
        "件数", compute="_compute_packaging_qty", store=True)
    packaging_weight = fields.Float(
        "包装毛重", related="packaging.weight", store=True)
    packaging_net_weight = fields.Float(
        "包装净重", related="packaging.net_weight", store=True)
    packaging_volume = fields.Float(
        "包装体积", related="packaging.volume", store=True)
    total_packaging_weight = fields.Float(
        "总包装毛重", compute="_compute_total", store=True)
    total_packaging_net_weight = fields.Float(
        "总包装净重", compute="_compute_total", store=True)
    total_packaging_volume = fields.Float(
        "总包装体积", compute="_compute_total", store=True)