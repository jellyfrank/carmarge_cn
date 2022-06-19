#!/usr/bin/python3
# @Time    : 2020-11-17
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class res_config_settings(models.TransientModel):

    _inherit = "res.config.settings"

    history_duration = fields.Integer(
        "History Prcie Compute Duration", config_parameter="history.duration", default=6)
    history_limit = fields.Integer(
        "History Price Limited Count", config_parameter="history.limit", default=0)
