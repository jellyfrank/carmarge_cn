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

    height = fields.Float("包装高(CM)")
    length = fields.Float("包装长(CM)")
    net_weight = fields.Float("包装净重(KG)")
    width = fields.Float("包装宽(CM)")
    weight = fields.Float("包装毛重(CM)")
    volume   = fields.Float("包装体积(CM3)", compute="_get_volume", digits=(16,4))