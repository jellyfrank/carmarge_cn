#!/usr/bin/python3
# @Time    : 2022-01-25
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class purchase_order(models.Model):

    _inherit = "purchase.order"

    @api.depends('order_line.price_total', "delivery_cost", "discount_manual")
    def _amount_all(self):
        super(purchase_order, self)._amount_all()
        delivery_product_id = self.env.ref(
            "carmarge_sale_cn.service_delivery_cost")
        discount_product_id = self.env.ref(
            "carmarge_sale_cn.service_discount")
        # 添加运费和优惠
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                if line.product_id not in [delivery_product_id.product_variant_id,discount_product_id.product_variant_id]:
                    amount_untaxed += line.price_subtotal
                    amount_tax += line.price_tax
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            order.update({
                "amount_total": order.amount_total + order.delivery_cost - order.discount_manual,
                "amount_untaxed":currency.round(amount_untaxed),
                "amount_tax":currency.round(amount_tax),
            })

    def _prepare_invoice(self):
        data = super(purchase_order,self)._prepare_invoice()
        data.update({
            "delivery_cost": self.delivery_cost,
            "discount_manual": self.discount_manual
        })
        return data

    def _set_sale_name(self,sale_id):
        """关联销售订单"""
        # 搜索当前销售订单关联的采购订单数量
        purchase_count = self.sudo().search([('sale_id','=',sale_id)])
        if not purchase_count:
            index = 1
        else:
            index = len(purchase_count)+1

        sale_order = self.env['sale.order'].browse(int(sale_id))

        return f"{sale_order.name}{index:02}"

    @api.depends("order_line.product_id", "order_line.price_unit")
    def _compute_delivery_discount(self):
        """计算海运费和优惠"""
        delivery_product_id = self.env.ref(
            "carmarge_sale_cn.service_delivery_cost")
        discount_product_id = self.env.ref(
            "carmarge_sale_cn.service_discount")
        if not delivery_product_id:
            self.delivery_cost = 0
        if not discount_product_id:
            self.discount_manual = 0

        if delivery_product_id.product_variant_id in self.order_line.product_id:
            delivery_line = self.order_line.filtered(
                lambda l: l.product_id == delivery_product_id.product_variant_id)
            self.delivery_cost = delivery_line.price_subtotal
        else:
            self.delivery_cost = 0

        if not discount_product_id.product_variant_id in self.order_line.product_id:
            self.discount_manual = 0

        discount_line = self.order_line.filtered(
            lambda l: l.product_id == discount_product_id.product_variant_id)
        self.discount_manual = discount_line.price_subtotal

    delivery_cost = fields.Monetary("运费",compute="_compute_delivery_discount", store=True)
    discount_manual = fields.Monetary("优惠",compute="_compute_delivery_discount", store=True)
    sale_id = fields.Many2one("sale.order",string="销售单")


    @api.model
    def create(self,vals):
        if vals.get("sale_id",None):
            vals['name'] = self._set_sale_name(vals['sale_id'])
        return super(purchase_order,self).create(vals)

    def write(self,vals):
        if vals.get("sale_id",None):
            vals['name'] = self._set_sale_name(vals['sale_id'])
        return super(purchase_order,self).write(vals)

class purchase_order_line(models.Model):

    _inherit = "purchase.order.line"

    @api.depends("order_id.delivery_cost", "order_id.discount_manual")
    def _compute_line(self):
        for line in self:
            line.delivery_cost_line = line.order_id.delivery_cost / \
                len(line.order_id.order_line)
            line.discount_manual_line = line.order_id.discount_manual / \
                len(line.order_id.order_line)

    @api.depends("product_id","books/")
    def _get_product_packaging(self):
        """获取包裹数量"""
        # 取产品库存包装信息中的第一条
        for line in self:
            # line.packaging = line.product_id.packaging_ids[0] if line.product_id.packaging_ids else None
            line.packaging = line.product_packaging

    @api.depends("packaging", "product_qty")
    def _compute_packaging_qty(self):
        """计算包裹数量"""
        for line in self:
            line.packaging_qty = line.product_qty / \
                line.packaging.qty if line.packaging.qty != 0 else 0

    @api.depends("packaging", "product_qty")
    def _compute_total(self):
        for line in self:
            line.total_packaging_weight = line.packaging_qty * line.packaging.weight
            line.total_packaging_volume = line.packaging_qty * line.packaging.volume
            line.total_packaging_net_weight = line.packaging_qty * line.packaging_net_weight

    @api.onchange('product_id')
    def _onchange_product_packaging(self):
        '''
        根据产品获取包装规格
        '''
        product_ids = []
        self.packaging=False
        product_data = self.product_id
        if product_data and product_data.packaging_ids:
            for pack in product_data.packaging_ids:
                product_ids.append(pack.id)
        return {
            'domain':{
                'packaging':[('id','in',product_ids)]
            }
        }


    delivery_cost_line = fields.Monetary(
        "运费", compute="_compute_line", store=True)
    discount_manual_line = fields.Monetary(
        "优惠", compute="_compute_line", store=True)
    packaging = fields.Many2one(
        "product.packaging", string="包装规格")
    packaging_qty = fields.Float(
        "件数", compute="_compute_packaging_qty", store=True)
    packaging_weight = fields.Float(
        "包装毛重", related="packaging.weight", store=True)
    packaging_net_weight = fields.Float(
        "包装净重", related="packaging.net_weight", store=True)
    packaging_volume = fields.Float(
        "包装体积", related="packaging.volume", store=True)
    total_packaging_weight = fields.Float(
        "总包装毛重", compute="_compute_total", store=True)
    total_packaging_net_weight = fields.Float(
        "总包装净重", compute="_compute_total", store=True)
    total_packaging_volume = fields.Float(
        "总包装体积", compute="_compute_total", store=True)
    weight = fields.Float("毛重", related="product_id.weight")
    net_weight = fields.Float("净重", related="product_id.net_weight")
    volume = fields.Float("体积", related="product_id.volume")
