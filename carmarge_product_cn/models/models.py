#!/usr/bin/python3
# @Time    : 2022-01-24
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class product_template(models.Model):

    _inherit = "product.template"

    default_code = fields.Char(string="配件编号")
    net_weight = fields.Float(string="净重")
    weight = fields.Float(string="毛重")
    comm_check = fields.Boolean("是否商检", default=False)
    type = fields.Selection(default="product")
    brand = fields.Many2many("product.brand",string="适用")

class product_brand(models.Model):

    _name = "product.brand"

    name = fields.Char("Product Brand")

