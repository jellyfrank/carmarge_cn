#!/usr/bin/python3
# @Time    : 2021-12-17
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class sale_order_line(models.Model):

    _inherit="sale.order.line"

    product_code = fields.Char(string="Part No.", related="product_id.default_code")