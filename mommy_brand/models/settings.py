#!/usr/bin/python3
# @Time    : 2021-12-15
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class res_config_settings(models.TransientModel):

    _inherit = "res.config.settings"

    mommy_title = fields.Char(string="System Title",
                              config_parameter="mommy.title", default="Odoo")
    mommy_show_document = fields.Boolean(
        "Show Documents", config_parameter="mommy.documents")
    mommy_show_support = fields.Boolean(
        "Show Support", config_parameter="mommy.support")
    mommy_show_shortcuts = fields.Boolean(
        "Show Shortcuts", config_parameter="mommy.shortcuts")
    mommy_show_odoo_account = fields.Boolean(
        "Show Odoo Account", config_parameter="mommy.account")

    @api.model
    def get_personal_center(self):
        cfg_obj = self.env['ir.config_parameter'].sudo()
        show_documents = cfg_obj.get_param("mommy.documents")
        show_support = cfg_obj.get_param("mommy.support")
        show_shortcuts = cfg_obj.get_param("mommy.shortcuts")
        show_account = cfg_obj.get_param("mommy.account")
        return [show_documents, show_support, show_shortcuts, show_account]
