#!/usr/bin/python3
# @Time    : 2022-05-11
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class stock_picking(models.Model):
    _inherit="stock.picking"

    def button_fill_quantity(self):
        """填充需求数量"""
        for move in self.move_ids_without_package:
            move.quantity_done = move.product_uom_qty