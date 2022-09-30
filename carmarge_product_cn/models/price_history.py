#!/usr/bin/python3
# @Time    : 2022-06-17
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class product_price_history(models.TransientModel):
    _name = "product.price.history"

    sale_order = fields.Many2one("sale.order", string="销售订单")
    sale_date = fields.Datetime("销售日期")
    product_id = fields.Many2one("product.template", string="产品")
    product_uom = fields.Many2one("uom.uom", string="单位")
    currency_id = fields.Many2one('res.currency',string='币种')
    quantity = fields.Float("数量")
    price_list = fields.Many2one("product.pricelist",string="价格表")
    price = fields.Monetary("单价")
    partner_id = fields.Many2one("res.partner", string="客户")
    currency_id = fields.Many2one('res.currency',string='currency')


