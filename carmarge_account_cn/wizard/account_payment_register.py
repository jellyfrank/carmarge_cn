#!/usr/bin/python3
# @Time    : 2022-05-22
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _

class account_payment_register(models.TransientModel):
    _inherit = "account.payment.register"

    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id', 'payment_date')
    def _compute_amount(self):
        super(account_payment_register,self)._compute_amount()
        for wizard in self:
            wizard.amount -= 