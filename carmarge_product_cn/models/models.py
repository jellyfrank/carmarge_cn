#!/usr/bin/python3
# @Time    : 2022-01-24
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class product_template(models.Model):

    _inherit = "product.template"

    brand = fields.Many2many("product.brand",string="适用")
    comm_check = fields.Boolean("是否商检", default=False)
    default_code = fields.Char(string="配件编号")
    is_brand_package = fields.Boolean("是否品牌包装")
    length = fields.Float("长")
    width = fields.Float("宽")
    height = fields.Float("高")
    net_weight = fields.Float(string="净重")
    weight = fields.Float(string="毛重")
    type = fields.Selection(default="product")

class product_brand(models.Model):

    _name = "product.brand"

    name = fields.Char("Product Brand")

