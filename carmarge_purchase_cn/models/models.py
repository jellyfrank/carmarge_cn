#!/usr/bin/python3
# @Time    : 2022-01-25
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _
from odoo.models import NewId
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang, get_lang, format_amount
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

RECEIVE_STATES = [
    ('none','未入库'),
    ('partial','部分入库'),
    ('done','全部入库')
]


class purchase_order(models.Model):

    _inherit = "purchase.order"

    @api.depends('order_line.price_total', "delivery_cost", "discount_manual")
    def _amount_all(self):
        super(purchase_order, self)._amount_all()
        delivery_product_id = self.env.ref(
            "carmarge_purchase_cn.service_delivery_cost")
        discount_product_id = self.env.ref(
            "carmarge_purchase_cn.service_discount")
        # 添加运费和优惠
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                if line.product_id not in [delivery_product_id.product_variant_id,discount_product_id.product_variant_id]:
                    amount_untaxed += line.price_subtotal
                    amount_tax += line.price_tax
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
            data ={
                "amount_total": amount_untaxed + order.amount_tax + order.delivery_cost + order.discount_manual,
                "amount_untaxed":currency.round(amount_untaxed),
                "amount_tax":currency.round(amount_tax),
            }
            order.update(data)

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
        for po in self:
            delivery_product_id = po.env.ref(
                "carmarge_purchase_cn.service_delivery_cost")
            discount_product_id = po.env.ref(
                "carmarge_purchase_cn.service_discount")
            if not delivery_product_id:
                po.delivery_cost = 0
            if not discount_product_id:
                po.discount_manual = 0

            if delivery_product_id.product_variant_id in po.order_line.product_id:
                delivery_line = po.order_line.filtered(
                    lambda l: l.product_id == delivery_product_id.product_variant_id)
                po.delivery_cost = delivery_line.price_subtotal
            else:
                po.delivery_cost = 0

            if not discount_product_id.product_variant_id in po.order_line.product_id:
                po.discount_manual = 0

            discount_line = po.order_line.filtered(
                lambda l: l.product_id == discount_product_id.product_variant_id)
            po.discount_manual = discount_line.price_subtotal

    def _add_supplier_to_product(self):
        # Add the partner in the supplier list of the product if the supplier is not registered for
        # this product. We limit to 10 the number of suppliers for a product to avoid the mess that
        # could be caused for some generic products ("Miscellaneous").
        for line in self.order_line:
            # Do not add a contact as a supplier
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            if line.product_id and partner not in line.product_id.seller_ids.mapped('name') and len(line.product_id.seller_ids) <= 10:
                # Convert the price in the right currency.
                currency = partner.property_purchase_currency_id or self.env.company.currency_id
                price = self.currency_id._convert(line.price_unit, currency, line.company_id, line.date_order or fields.Date.today(), round=False)
                # Compute the price for the template's UoM, because the supplier's UoM is related to that UoM.
                if line.product_id.product_tmpl_id.uom_po_id != line.product_uom:
                    default_uom = line.product_id.product_tmpl_id.uom_po_id
                    price = line.product_uom._compute_price(price, default_uom)

                supplierinfo = {
                    'name': partner.id,
                    'sequence': max(line.product_id.seller_ids.mapped('sequence')) + 1 if line.product_id.seller_ids else 1,
                    'min_qty': 0.0,
                    'price': price,
                    'currency_id': currency.id,
                    'delay': 0,
                    "min_qty": line.product_qty,
                    "date_start": datetime.now(),
                    "date_end": line.order_id.date_order
                }
                # In case the order partner is a contact address, a new supplierinfo is created on
                # the parent company. In this case, we keep the product name and code.
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order and line.order_id.date_order.date(),
                    uom_id=line.product_uom)
                if seller:
                    supplierinfo['product_name'] = seller.product_name
                    supplierinfo['product_code'] = seller.product_code
                vals = {
                    'seller_ids': [(0, 0, supplierinfo)],
                }
                try:
                    line.product_id.write(vals)
                except AccessError:  # no write access rights -> just ignore
                    break

    @api.depends("order_line.receive_state")
    def _compute_receive_state(self):
        """计算入库状态"""
        for po in self:
            if not po.order_line:
                po.receive_state = 'none'
            else:
                states = list(set(po.order_line.filtered(lambda l:l.receive_state in ('none','done')).mapped("receive_state")))
                if len(states) == 1 and states[0] == 'none':
                    po.receive_state = 'none'
                elif len(states) == 1 and states[0] == 'done':
                    po.receive_state = 'done'
                else:
                    po.receive_state = 'partial'

    @api.depends("invoice_ids.state","invoice_ids.amount_residual")
    def _compute_amount(self):
        """计算到期金额和已付金额"""
        for po in self:
            total = abs(sum([invoice_id.amount_total_signed for invoice_id in po.invoice_ids if invoice_id.state == 'posted']))
            po.due_amount = abs(sum([invoice_id.amount_residual_signed for invoice_id in po.invoice_ids if invoice_id.state == 'posted']))
            po.paid_amount = total - po.due_amount


    delivery_cost = fields.Monetary("运费",compute="_compute_delivery_discount", store=True)
    discount_manual = fields.Monetary("优惠",compute="_compute_delivery_discount", store=True)
    sale_id = fields.Many2one("sale.order",string="销售单")
    receive_state = fields.Selection(RECEIVE_STATES,string="入库状态",compute="_compute_receive_state", store=True)
    paid_amount = fields.Monetary("已付金额", compute="_compute_amount",store=True)
    due_amount = fields.Monetary("到期金额", compute="_compute_amount",store=True)

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
        
    @api.onchange("product_id")
    def _onchange_product_id(self):
        """产品发生变化时"""
        product_ids = []
        for line in self.order_id.order_line:
            if not line.product_id:
                continue
            if line.product_id.id == self.product_id.id:
                if isinstance(line.id, NewId):
                    if line.id.ref or line.id.origin:
                        product_ids.append(line.product_id.id)
                else:
                    product_ids.append(line.product_id.id)
        if len(product_ids)>=2:
            raise UserError(f"产品:{self.product_id.display_name}已经存在于明细行中！")

    @api.depends("product_qty","qty_received")
    def _compute_receive_state(self):
        """计算接收状态"""
        for line in self.filtered(lambda order: order.product_id.type != 'service'):
            if line.qty_received == 0:
                line.receive_state = 'none'
            elif line.product_qty > line.qty_received:
                line.receive_state = 'partial'
            else:
                line.receive_state = 'done'

    delivery_cost_line = fields.Monetary("运费", compute="_compute_line", store=True)
    discount_manual_line = fields.Monetary("优惠", compute="_compute_line", store=True)
    packaging = fields.Many2one("product.packaging", string="包装规格")
    packaging_qty = fields.Float("件数", compute="_compute_packaging_qty", store=True)
    packaging_weight = fields.Float("包装毛重", related="packaging.weight", store=True)
    packaging_net_weight = fields.Float("包装净重", related="packaging.net_weight", store=True)
    packaging_volume = fields.Float("包装体积", related="packaging.volume", store=True)
    receive_state = fields.Selection(RECEIVE_STATES,string="接收状态",compute="_compute_receive_state",store=True)
    total_packaging_weight = fields.Float("总包装毛重", compute="_compute_total", store=True)
    total_packaging_net_weight = fields.Float("总包装净重", compute="_compute_total", store=True)
    total_packaging_volume = fields.Float("总包装体积", compute="_compute_total", store=True)
    weight = fields.Float("毛重", related="product_id.weight")
    net_weight = fields.Float("净重", related="product_id.net_weight")
    volume = fields.Float("体积", related="product_id.volume")
    translate_name = fields.Char(string="英文名称", related="product_id.translate_name")

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return
        params = {'order_id': self.order_id}
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order.date(),
            uom_id=self.product_uom,
            params=params)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price,
                                                                             self.product_id.supplier_taxes_id,
                                                                             self.taxes_id,
                                                                             self.company_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id._convert(
                price_unit, self.order_id.currency_id, self.order_id.company_id, self.date_order or fields.Date.today())

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        # self.price_unit = price_unit
        product_ctx = {'seller_id': seller.id, 'lang': get_lang(self.env, self.partner_id.lang).code}
        self.name = self._get_product_purchase_description(self.product_id.with_context(product_ctx))
