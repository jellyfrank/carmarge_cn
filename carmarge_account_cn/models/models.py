#!/usr/bin/python3
# @Time    : 2022-05-20
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class account_move(models.Model):
    _inherit="account.move"
    
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        "delivery_cost",
        "discount_manual")
    def _compute_amount(self):
        super(account_move,self)._compute_amount()
        for move in self:
            # if move.move_type == "in_invoice":
            # 减掉明细行多算的 运费和优惠
            move.amount_untaxed -= (move.delivery_cost + move.discount_manual)
            # move.amount_total = move.amount_total - move.delivery_cost - move.discount_manual
            # move.amount_total = move.amount_total + move.delivery_cost - move.discount_manual
            move.amount_total = move.amount_untaxed +move.amount_tax + move.delivery_cost - move.discount_manual
            # move.· = move.amount_total

    @api.depends("invoice_line_ids.product_id", "invoice_line_ids.price_unit")
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

        if delivery_product_id.product_variant_id in self.invoice_line_ids.product_id:
            delivery_line = self.invoice_line_ids.filtered(
                lambda l: l.product_id == delivery_product_id.product_variant_id)
            self.delivery_cost = delivery_line.price_subtotal
        else:
            self.delivery_cost = 0

        if not discount_product_id.product_variant_id in self.invoice_line_ids.product_id:
            self.discount_manual = 0

        discount_line = self.invoice_line_ids.filtered(
            lambda l: l.product_id == discount_product_id.product_variant_id)
        self.discount_manual = discount_line.price_subtotal

    delivery_cost = fields.Monetary("运费", compute="_compute_delivery_discount",store=True)
    discount_manual = fields.Monetary("优惠",compute="_compute_delivery_discount",store=True)