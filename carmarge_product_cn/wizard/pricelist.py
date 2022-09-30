#!/usr/bin/python3
# @Time    : 2022-09-05
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class carmarge_pricelist_wizard(models.TransientModel):
    _name = "carmarge.pricelist.wizard"
    _description = "批量添加产品到价格表向导"

    pricelist_id = fields.Many2one("product.pricelist", string="价格表")
    min_quantity = fields.Integer("最小数量")
    date_start = fields.Datetime("开始日期")
    date_end = fields.Datetime("结束日期")
    compute_price = fields.Selection([
        ('fixed', '固定价格'),
        ('percentage', '百分比'),
        ('formula', '公式')
    ], string="计算价格", default="fixed")
    base = fields.Selection([
        ('list_price', '销售价格'),
        ('standard_price', '成本'),
        ('pricelist', '其他价格表')
    ], string="基于", default="list_price")
    fixed_price = fields.Float("固定价格")
    price_discount = fields.Float("折扣")
    percent_price = fields.Float("比例")
    base_pricelist_id = fields.Many2one("product.pricelist", string="价格表")
    price_surcharge = fields.Float("价格附加费用")
    price_round = fields.Float("价格舍入")
    price_min_margin = fields.Float("最小毛利")
    price_max_margin = fields.Float("最大毛利")

    def button_confirm(self):
        """确认"""
        if self.active_model != 'product.template' or not self.active_records:
            return self.show_message("模型错误", "数据模型错误或没有选中任何数据")

        data = [(0,0,{
            "applied_on":"1_product",
            "product_tmpl_id": product_id.id,
            "min_quantity": self.min_quantity,
            "date_start":self.date_start,
            "date_end": self.date_end,
            "compute_price": self.compute_price,
            "base": self.base,
            "fixed_price": self.fixed_price,
            "price_discount": self.price_discount,
            "percent_price": self.percent_price,
            "base_pricelist_id": self.base_pricelist_id,
            "price_surcharge": self.price_surcharge,
            "price_min_margin": self.price_min_margin,
            "price_max_margin": self.price_max_margin
        }) for product_id in self.active_records]

        self.pricelist_id.item_ids = data