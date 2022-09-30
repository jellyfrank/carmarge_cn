#!/usr/bin/python3
# @Time    : 2022-07-28
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class product_pricelist_item(models.Model):
    _inherit = "product.pricelist.item"

    product_categ_id = fields.Many2one(
        "product.category", related="product_tmpl_id.categ_id", string="产品类别")
    default_code = fields.Char(
        related="product_tmpl_id.default_code", string="配件编码")
    qty_available = fields.Float(
        related="product_tmpl_id.qty_available", string="在手数量")
    virtual_available = fields.Float(
        related="product_tmpl_id.virtual_available", string="预测数量")
    purchased_qty = fields.Float(
        related="product_tmpl_id.purchased_product_qty", string="已采购")
    sales_count = fields.Float(related="product_tmpl_id.sales_count", string="已销售")
