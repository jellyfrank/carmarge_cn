#!/usr/bin/python3
# @Time    : 2022-01-24
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class product_template(models.Model):

    _inherit = "product.template"

    def _get_packaging(self):
        """"""
        for product in self:
            if not product.packaging_ids:
                product.packaging = None
            else:
                product.packaging = product.packaging_ids[0] if product.packaging_ids else None

    brand = fields.Many2many("product.brand", string="适用")
    comm_check = fields.Boolean("是否商检", default=False)
    default_code = fields.Char(string="配件编号")
    height = fields.Float("高")
    is_brand_package = fields.Boolean("是否品牌包装")
    length = fields.Float("长")
    net_weight = fields.Float(string="净重")
    packaging = fields.Many2one(
        "product.packaging", string="包装", compute="_get_packaging")
    packaging_length = fields.Float("包装长", related="packaging.length")
    packaging_width = fields.Float("包装宽", related="packaging.width")
    packaging_height = fields.Float("包装高", related="packaging.height")
    packaging_volume = fields.Float("包装体积", related="packaging.volume")
    packaging_net_weight = fields.Float("包装净重", related="packaging.net_weight")
    packaging_weight = fields.Float("包装毛重", related="packaging.weight")
    width = fields.Float("宽")
    weight = fields.Float(string="毛重")
    type = fields.Selection(default="product")


class product_brand(models.Model):

    _name = "product.brand"

    name = fields.Char("Product Brand")
