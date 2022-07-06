# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class list_preview_widget(models.Model):
#     _name = 'list_preview_widget.list_preview_widget'
#     _description = 'list_preview_widget.list_preview_widget'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
