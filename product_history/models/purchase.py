#!/usr/bin/python3
# @Time    : 2020-11-19
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class purchase_order_line(models.Model):

    _inherit = "purchase.order.line"

    activity_exception_icon = fields.Char(
        "Icon", help="Icon to indicate an exception activity.", default="fa-history")

    def _get_history_price(self):
        duration = int(self.env['ir.config_parameter'].sudo().get_param(
            "history.duration"))
        date_start = datetime.strftime(
            datetime.now()-relativedelta(months=duration), '%Y-%m-%d %H:%M:%S')
        date_end = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        limit = int(self.env['ir.config_parameter'].sudo(
        ).get_param("history.limit"))
        domain = [('product_id', '=', self.product_id.id),
                  ('state', 'in', ('purchase', 'done')), ('write_date', '>=', date_start), ('write_date', '<=', date_end)]
        if type(self.id) is int:
            domain.append(('id', '!=', self.id))
        _logger.debug(
            f"Searching product history price for purchase, product: {self.product_id.name}, domain:{domain}")
        lines = self.sudo().search(
            domain, limit=limit) if limit else self.sudo().search(domain)
        return ";".join(
            _(f"Order:{pre_line.order_id.name} Order Date:{pre_line.order_id.date_order} Price:{pre_line.price_unit}") for pre_line in lines)

    def _get_history_prices(self):
        """get purchase price of one product before."""

        for line in self:
            line.history_prices = line._get_history_price()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """return price history when product_id changes"""
        return {'value': {'history_prices': self._get_history_price()}}

    history_prices = fields.Char(
        "History Purchase Prices", compute="_get_history_prices")
