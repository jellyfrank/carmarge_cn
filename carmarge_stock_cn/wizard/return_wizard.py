#!/usr/bin/python3
# @Time    : 2022-05-11
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _

class stock_return_piciking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        res = super(stock_return_piciking,self)._prepare_stock_return_picking_line_vals_from_move(stock_move)
        res['quantity'] = 0
        return res

    def button_delete(self):
        """删除选中的行"""
        for line in self.product_return_moves:
            if line.selected:
                line.unlink()



class stock_return_picking_line(models.TransientModel):
    _inherit="stock.return.picking.line"

    selected = fields.Boolean("选择")

    
                