#!/usr/bin/python3
from odoo import api, fields, models, _, exceptions

class res_company(models.Model):
    _inherit = "res.company"

    watermark_img = fields.Binary(string="水印图片")
