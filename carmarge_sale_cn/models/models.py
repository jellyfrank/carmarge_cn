#!/usr/bin/python3
# @Time    : 2022-01-25
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class sale_order(models.Model):

    _inherit = "sale.order"

    @api.depends('order_line.price_total', "delivery_cost", "discount_manual")
    def _amount_all(self):
        super(sale_order, self)._amount_all()
        # 添加运费和优惠
        # 当前减去order.amount_tax(税金)是因为客户输入的单价已经是含税单价了，所以把系统本身加上的税金再在这里减去
        for order in self:
            order.update({
                "amount_total": order.amount_total + order.delivery_cost - order.discount_manual
            })



    delivery_cost = fields.Monetary("海运费")
    discount_manual = fields.Monetary("优惠")
    port_city = fields.Many2one("carmarge.ship.city","发货地")


    @api.model
    def create(self, vals):
        partner_id = self.env['res.partner'].sudo().browse(vals.get('partner_id'))
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            vals_name = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _('New')
            if vals_name!='New':
                vals['name'] = partner_id.country_id.code + vals_name

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist.id)
        result = super(sale_order, self).create(vals)
        return result


class sale_order_line(models.Model):

    _inherit = "sale.order.line"

    @api.depends("order_id.delivery_cost", "order_id.discount_manual")
    def _compute_line(self):
        for line in self:
            line.delivery_cost_line = line.order_id.delivery_cost / \
                len(line.order_id.order_line)
            line.discount_manual_line = line.order_id.discount_manual / \
                len(line.order_id.order_line)

    @api.depends("product_id","product_packaging")
    def _get_product_packaging(self):
        """获取包裹数量"""
        # 取产品库存包装信息中的第一条
        for line in self:
            # line.packaging = line.product_id.packaging_ids[0] if line.product_id.packaging_ids else None
            line.packaging = line.product_packaging

    @api.depends("packaging", "product_qty","product_packaging","product_uom_qty")
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

    def _compute_sale_price_update_group(self):
        self.group_use_sale_price_update = self.user_has_groups('carmarge_sale_cn.group_use_sale_price_update')

    @api.model
    def _default_sale_order_update(self):
        return self.user_has_groups('carmarge_sale_cn.group_use_sale_price_update')

    delivery_cost_line = fields.Monetary(
        "运费", compute="_compute_line", store=True)
    discount_manual_line = fields.Monetary(
        "优惠", compute="_compute_line", store=True)
    packaging = fields.Many2one(
        "product.packaging", string="包装规格", compute="_get_product_packaging")
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

    group_use_sale_price_update = fields.Boolean(string="单价是否可编辑", default=_default_sale_order_update, compute="_compute_sale_price_update_group")


