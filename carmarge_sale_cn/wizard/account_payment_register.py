#!/usr/bin/python3
# @Time    : 2022-04-09
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class account_payment_register(models.TransientModel):
    _inherit="account.payment.register"

    @api.model
    def _get_wizard_values_from_batch(self, batch_result):
        """
        计算支付金额 加上运费和优惠
        """
        res = super(account_payment_register,self)._get_wizard_values_from_batch(batch_result)
        # move = self.line_ids[0].move_id
        # res['source_amount_currency'] = res['source_amount_currency'] + move.delivery_cost - move.discount_manual
        return res

