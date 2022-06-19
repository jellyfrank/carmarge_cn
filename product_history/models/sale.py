#!/usr/bin/python3
# @Time    : 2020-11-17
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class sale_order_line(models.Model):

    _inherit = "sale.order.line"

    activity_exception_icon = fields.Char(
        "Icon", help="Icon to indicate an exception activity.", default="fa-history")

    @api.depends("product_id")
    def _get_history_price(self):
        """get history price of one product."""
        duration = int(self.env['ir.config_parameter'].sudo().get_param("history.duration"))
        date_start = datetime.strftime(
            datetime.now()-relativedelta(months=duration), '%Y-%m-%d %H:%M:%S')
        date_end = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        limit = int(self.env['ir.config_parameter'].sudo(
        ).get_param("history.limit"))
        for line in self:
            if type(line.id) == int:
                domain = [('product_id', '=', line.product_id.id), ('id', '!=', line.id),
                        ('state', 'in', ('sale', 'done')), ('write_date', '>=', date_start), ('write_date', '<=', date_end)]
            else:
                domain = [('product_id', '=', line.product_id.id),('state', 'in', ('sale', 'done')), ('write_date', '>=', date_start), ('write_date', '<=', date_end)]
            lines = self.sudo().search(
                domain, limit=limit) if limit else self.sudo().search(domain)
            line.history_prices = ";".join(
                _(f"Order:{pre_line.order_id.name} Customer:{pre_line.order_id.partner_id.name} Order Date:{pre_line.order_id.date_order} Price:{pre_line.price_unit}") for pre_line in lines)

    history_prices = fields.Char(
        "History Sale Prices", compute="_get_history_price")
