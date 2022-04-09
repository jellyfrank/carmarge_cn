#!/usr/bin/python3

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_sale_order(self):
        """
        获取关联的销售订单
        """
        for move in self:
            if not move.invoice_line_ids:
                move.sale_order = None
            else:
                move.sale_order = move.invoice_line_ids[0].sale_line_ids[0].order_id
            



    sale_order = fields.Many2one("sale.order",string="关联的销售订单", compute="_compute_sale_order")

    def _get_sale_order_amount(self):
        '''
        获取销售订单的总金额
        '''
        self.ensure_one()
        report_arr = []
        sale_order = self.env['sale.order'].search([('name','=',self.invoice_origin)])
        if sale_order:
            report_arr.append({
                'amount_total':sale_order.amount_total,
                'amount_untaxed':sale_order.amount_untaxed,
                'amount_tax':sale_order.amount_tax,
                'delivery_cost':sale_order.delivery_cost,
            })
        return report_arr


    def _get_deposit_default_product_id(self):
        product = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        product_id = self.env['product.product'].browse(int(product)).exists()
        return product_id.id
