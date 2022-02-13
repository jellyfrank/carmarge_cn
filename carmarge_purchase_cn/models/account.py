#!/usr/bin/python3
# @Time    : 2022-02-13
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class account_move(models.Model):

    _inherit = "account.move"

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
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        super(account_move,self)._compute_amount()
        for move in self:
            move.amount_total = move.amount_total + move.delivery_cost - move.discount_manual

    delivery_cost = fields.Monetary("运费")
    discount_manual = fields.Monetary("优惠")
    amount_total = fields.Monetary(string='Total', store=True, readonly=True,
        compute='_compute_amount',
        inverse='_inverse_amount_total')
