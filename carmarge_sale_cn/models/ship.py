#!/usr/bin/python3
# @Time    : 2022-03-04
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class carmarge_ship_city(models.Model):
    _name = "carmarge.ship.city"
    _description = "发货地"

    name = fields.Char("名称")
