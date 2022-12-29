#!/usr/bin/python3
# @Time    : 2022-12-13
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _

SPLIT_METHOD = [
    # ('equal', 'Equal'),
    # ('by_quantity', 'By Quantity'),
    ('by_current_cost_price', 'By Current Cost'),
    ('by_weight', 'By Weight'),
    ('by_volume', 'By Volume'),
]

class sale_cost(models.Model):
    _name = "sale.cost"
    _description = "销售成本均摊"

    cost = fields.Float("成本")
    is_splited = fields.Boolean("是否均摊过", default=False)
    order_id = fields.Many2one("sale.order", string="销售订单")
    product_id = fields.Many2one("product.product",string="产品", domain="[('type','=','service')]")
    split_method = fields.Selection(
        SPLIT_METHOD,
        string='Split Method',
        required=True,
        help="Equal : Cost will be equally divided.\n"
             "By Quantity : Cost will be divided according to product's quantity.\n"
             "By Current cost : Cost will be divided according to product's current cost.\n"
             "By Weight : Cost will be divided depending on its weight.\n"
             "By Volume : Cost will be divided depending on its volume.")


    def button_split(self):
        """费用均摊"""
        if  self.split_method == "equal":
            additional_cost = self.cost / len(self.order_id.order_line)
            for line in self.order_id.order_line:
                line.price_unit += additional_cost
        elif self.split_method == "by_quantity":
            qty = sum(self.order_id.order_line.mapped("product_uom_qty"))
            additional_cost = self.cost / qty if qty else 0
            for line in self.order_id.order_line:
                line.price_unit  += additional_cost * line.product_uom_qty
        elif self.split_method == 'by_current_cost_price':
            price = sum(self.order_id.order_line.mapped("product_id").mapped("standard_price"))
            additional_cost = self.cost / price if price else 0
            for line in self.order_id.order_line:
                line.price_unit  += additional_cost * line.product_id.standard_price
        elif self.split_method == "by_weight":
            weight = sum(self.order_id.order_line.mapped("product_id").mapped("weight"))
            additional_cost = self.cost / weight if weight else 0 
            for line in self.order_id.order_line:
                line.price_unit += additional_cost * line.product_id.weight
        else:
            vol = sum(self.order_id.order_line.mapped("product_id").mapped("volume"))
            additional_cost = self.cost / vol if vol else 0
            for line in self.order_id.order_line:
                line.price_unit += additional_cost * line.product_id.volume
        self.is_splited = True
    

