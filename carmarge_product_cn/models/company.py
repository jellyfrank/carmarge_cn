#!/usr/bin/python3
# @Time    : 2022-03-04
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class res_partner_bank(models.Model):
    _inherit = "res.partner.bank"

    swift_code = fields.Char("SWIFT编码")
    address = fields.Char("银行地址")


class res_company(models.Model):
    _inherit = "res.company"

    @api.depends("partner_id", "partner_id.bank_ids")
    def _compute_bank(self):
        """获取银行信息"""
        if self.partner_id.bank_ids:
            self.bank_info = self.partner_id.bank_ids[0]
        else:
            self.bank_info = None

    bank_info = fields.Many2one(
        "res.partner.bank", compute="_compute_bank", string="银行信息")
    acc_number = fields.Char("银行账号", related="bank_info.acc_number")
    bank_id = fields.Many2one("res.bank", string="银行",
                              related="bank_info.bank_id")
    acc_type = fields.Selection(
        lambda x: x.env['res.partner.bank'].get_supported_account_types(), related="bank_info.acc_type")
    bank_currency_id = fields.Many2one(
        "res.currency", string="币种", related="bank_info.currency_id")
    bank_partner_id = fields.Many2one(
        "res.partner", string='持有人', related="bank_info.partner_id")
    acc_holder_name = fields.Char("持有人姓名", related="bank_info.acc_holder_name")
    swift_code = fields.Char("SWIFT编码", related="bank_info.swift_code")
    address = fields.Char("银行地址", related="bank_info.address")
