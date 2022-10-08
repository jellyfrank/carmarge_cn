#!/usr/bin/python3
# @Time    : 2022-10-07
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class ir_actions_report(models.Model):
    _inherit="ir.actions.report"

    nickname = fields.Char("Nick Name")