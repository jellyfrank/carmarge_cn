# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Selection(string='联系人类型', selection=[(
        'distributor', '经销商'), ('fleet', '终端客户'), ('supplier', '供应商')])

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        value = self.env.context.get('partner_type')
        newValue = 'distributor' if value == None else value
        res.update({
            'partner_type': newValue,
        })
        return res
