# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class carmarge_account_cn(models.Model):
#     _name = 'carmarge_account_cn.carmarge_account_cn'
#     _description = 'carmarge_account_cn.carmarge_account_cn'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
