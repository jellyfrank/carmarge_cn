#!/usr/bin/python3
# @Time    : 2022-01-25
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _, exceptions
from odoo.models import NewId
from odoo.exceptions import UserError

DELIVERY_STATES = [
    ('no','未交货'),
    ('partial','部分交货'),
    ('all','全部交货')
]


class sale_order(models.Model):

    _inherit = "sale.order"

    @api.depends('order_line.price_total', "delivery_cost", "discount_manual")
    def _amount_all(self):
        super(sale_order, self)._amount_all()
        # 添加运费和优惠
        for order in self:
            order.update({
                "amount_total": order.amount_payment + order.delivery_cost + order.discount_manual
            })

    @api.depends("order_line.product_id", "order_line.price_unit")
    def _compute_delivery_discount(self):
        """计算海运费和优惠"""
        for order in self:
            delivery_product_id = order.env.ref(
                "carmarge_purchase_cn.service_delivery_cost")
            discount_product_id = order.env.ref(
                "carmarge_purchase_cn.service_discount")
            if not delivery_product_id:
                order.delivery_cost = 0
            if not discount_product_id:
                order.discount_manual = 0

            if delivery_product_id.product_variant_id in order.order_line.product_id:
                delivery_line = order.order_line.filtered(
                    lambda l: l.product_id == delivery_product_id.product_variant_id)
                order.delivery_cost = delivery_line.price_subtotal
            else:
                order.delivery_cost = 0

            if not discount_product_id.product_variant_id in order.order_line.product_id:
                order.discount_manual = 0

            discount_line = order.order_line.filtered(
                lambda l: l.product_id == discount_product_id.product_variant_id)
            order.discount_manual = discount_line.price_subtotal

    @api.depends("order_line.price_total")
    def _compute_amount_payment(self):
        '''计算货款'''
        delivery_product_id = self.env.ref(
            "carmarge_purchase_cn.service_delivery_cost")
        discount_product_id = self.env.ref(
            "carmarge_purchase_cn.service_discount")
        amount = 0
        for line in self.order_line:
            if line.product_id not in [delivery_product_id.product_variant_id,discount_product_id.product_variant_id]:
                amount = amount + line.price_total
        self.update({
            "amount_payment":amount
        })

    @api.depends('order_line.margin', 'amount_payment','discount_manual')
    def _compute_margin(self):
        if not all(self._ids):
            for order in self:
                order.margin = sum(order.order_line.mapped('margin'))
                payment = order.amount_payment - abs(order.discount_manual)
                order.margin_percent = order.margin / payment if payment != 0 else 0
        else:
            self.env["sale.order.line"].flush(['margin'])
            # On batch records recomputation (e.g. at install), compute the margins
            # with a single read_group query for better performance.
            # This isn't done in an onchange environment because (part of) the data
            # may not be stored in database (new records or unsaved modifications).
            grouped_order_lines_data = self.env['sale.order.line'].read_group(
                [
                    ('order_id', 'in', self.ids),
                ], ['margin', 'order_id'], ['order_id'])
            mapped_data = {m['order_id'][0]: m['margin'] for m in grouped_order_lines_data}
            for order in self:
                order.margin = mapped_data.get(order.id, 0.0)
                order.margin_percent = order.amount_untaxed and order.margin / order.amount_untaxed

    @api.depends("order_line.delivery_state")
    def _compute_delivery_state2(self):
        """交付状态"""
        for order in self:
            states = list(set(order.order_line.mapped("delivery_state")))
            if len(states) == 1 and states[0] == 'no':
                order.delivery_state = 'no'
            elif len(states) == 1 and states[0] == "all":
                order.delivery_state = 'all'
            else:
                order.delivery_state = 'partial' 

    @api.depends("invoice_ids.state","invoice_ids.amount_total")
    def _compute_amount(self):
        """计算应付金额"""
        # 计算销售订单的应付金额
        for order in self:
            amount_total = sum([invoice_id.amount_total for invoice_id in order.invoice_ids if invoice_id.state == 'posted'])
            residual_amount = sum([invoice_id.amount_residual for invoice_id in order.invoice_ids if invoice_id.state == 'posted'])
            order.paid_amount = amount_total - residual_amount
            order.due_amount = residual_amount


    delivery_cost = fields.Monetary(
        "海运费", compute="_compute_delivery_discount", store=True)
    discount_manual = fields.Monetary(
        "优惠", compute="_compute_delivery_discount", store=True)
    port_city = fields.Many2one("carmarge.ship.city", "发货地")
    incoterm = fields.Many2one(
        'account.incoterms', domain="[('code','in',['FOB','CIF'])]")
    incoterm_code = fields.Char("贸易术语code", related='incoterm.code')
    amount_payment = fields.Monetary("货款", compute="_compute_amount_payment", store=True)
    payment_term = fields.Char("付款条款", required=True)   
    delivery_state = fields.Selection(DELIVERY_STATES,string='交付状态',compute="_compute_delivery_state2",store=True)
    paid_amount = fields.Monetary("已付金额", compute="_compute_amount",store=True)
    due_amount = fields.Monetary("应付金额", compute="_compute_amount",store=True)
    

    @api.model
    def create(self, vals):
        partner_id = self.env['res.partner'].sudo().browse(
            vals.get('partner_id'))
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['date_order']))
            vals_name = self.env['ir.sequence'].next_by_code(
                'sale.order', sequence_date=seq_date) or _('New')
            if vals_name != 'New':
                vals['name'] = str(partner_id.country_id.code) + str(vals_name)

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault(
                'partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault(
                'partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault(
                'pricelist_id', partner.property_product_pricelist.id)
        result = super(sale_order, self).create(vals)
        return result

    def action_confirm(self):
        if self.state == 'draft':
            raise exceptions.Warning('当前报价单未发送报价！')
        result = super(sale_order, self).action_confirm()
        return result

    @api.onchange('pricelist_id')
    def _onchange_order_line_price_unit(self):
        if self.pricelist_id and self.partner_id and self.order_line:
            for line in self.order_line:
                line.product_id_change()

    def action_qita_send(self):
        self.state = 'sent'

    def _find_mail_template(self, force_confirmation_template=False):
        template_id = False

        if force_confirmation_template or (not self.env.context.get('proforma', False)):
            template_id = int(self.env['ir.config_parameter'].sudo(
            ).get_param('sale.default_confirmation_template'))
            template_id = self.env['mail.template'].search(
                [('id', '=', template_id)]).id
            if not template_id:
                template_id = self.env['ir.model.data'].xmlid_to_res_id(
                    'sale.mail_template_sale_confirmation', raise_if_not_found=False)
        if not template_id:
            template_id = self.env['ir.model.data'].xmlid_to_res_id(
                'sale.email_template_edi_sale', raise_if_not_found=False)

        return template_id


class sale_order_line(models.Model):

    _inherit = "sale.order.line"

    @api.depends("order_id.delivery_cost", "order_id.discount_manual")
    def _compute_line(self):
        for line in self:
            line.delivery_cost_line = line.order_id.delivery_cost / \
                len(line.order_id.order_line)
            line.discount_manual_line = line.order_id.discount_manual / \
                len(line.order_id.order_line)

    @api.depends("product_id", "product_packaging")
    def _get_product_packaging(self):
        """获取包裹数量"""
        # 取产品库存包装信息中的第一条
        for line in self:
            # line.packaging = line.product_id.packaging_ids[0] if line.product_id.packaging_ids else None
            line.packaging = line.product_packaging

    @api.depends("packaging", "product_qty", "product_packaging", "product_uom_qty")
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
        self.group_use_sale_price_update = self.user_has_groups(
            'carmarge_sale_cn.group_use_sale_price_update')

    def _prepare_invoice_line(self,**optional_values):
        """添加备注"""
        res = super(sale_order_line,self)._prepare_invoice_line(**optional_values)
        res['note'] = self.note
        return res

    @api.model
    def _default_sale_order_update(self):
        return self.user_has_groups('carmarge_sale_cn.group_use_sale_price_update')


    @api.constrains("product_id")
    def _check_product_id(self):
        """"校验产品唯一性"""
        lines = self.order_id.order_line.filtered(lambda line: line.product_id == self.product_id)
        if len(lines)>1:
            raise UserError(f"产品:{self.product_id.name}已经在明细中")

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

    @api.depends("product_qty","qty_delivered")
    def _compute_delivery_state(self):
        """交付状态"""
        for line in self:
            if line.qty_delivered == 0:
                line.delivery_state = 'no'
            elif 0<line.qty_delivered < line.product_qty:
                line.delivery_state = 'partial'
            else:
                line.devliery_state = 'done'

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

    group_use_sale_price_update = fields.Boolean(
        string="单价是否可编辑", default=_default_sale_order_update, compute="_compute_sale_price_update_group")
    note = fields.Char("备注")
    translate_name = fields.Char(string="英文名称",related="product_id.translate_name")
    delivery_state = fields.Selection(DELIVERY_STATES,string="交付状态",compute="_compute_delivery_state",store=True)
    

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )