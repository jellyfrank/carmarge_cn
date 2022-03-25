# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Selection(string='联系人类型', selection=[('distributor', '汽配经销商'), ('fleet', '车队'), ('supplier','供应商')],default='distributor')