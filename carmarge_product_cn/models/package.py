#!/usr/bin/python3
# @Time    : 2022-02-08
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class product_packaging(models.Model):

    _inherit="product.packaging"

    @api.depends("height","length","width")
    def _get_volume(self):
        """计算体积"""
        for packaging in self:
            packaging.volume = packaging.height * packaging.length * packaging.width / 10**6

    height = fields.Float("包装高")
    length = fields.Float("包装长")
    net_weight = fields.Float("包装净重")
    width = fields.Float("包装宽")
    weight = fields.Float("包装毛重")
    volume   = fields.Float("包装体积", compute="_get_volume")

