#!/usr/bin/python3
# @Time    : 2021-07-16
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class res_company(models.Model):

    _inherit = "res.company"

    def _get_model(self):
        model_name = self.env.context.get('model_name', False)
        if not model_name:
            self.emark = self.emark_invoice or self.emark_sale or self.emark_purchase or self.emark_delivery

        if model_name == 'sale.order':
            self.emark = self.emark_sale

        if model_name == 'purchase.order':
            self.emark = self.emark_purchase

        if model_name == "stock.picking":
            self.emark = self.emark_delivery

        if model_name == "account.move":
            self.emark = self.emark_invoice

    emark_sale = fields.Image("Sale Order Emark")
    emark_purchase = fields.Image("Purchase Order Emark")
    emark_delivery = fields.Image("Delivery Order Emark")
    emark_invoice = fields.Image("Invoice Emark")

    emark = fields.Image("Emark", compute="_get_model")
    emark_margin_left = fields.Integer("Margin Left(%)", default=90)
    emark_margin_top = fields.Integer("Margin Top(em)", default=-10)
    emark_img_size = fields.Integer("Image Size(px)", default=180)


class base_document_layout(models.TransientModel):

    _inherit = "base.document.layout"

    emark = fields.Image("Emark", related="company_id.emark", readonly=False)
    emark_margin_left = fields.Integer(
        "Margin Left(%)", related="company_id.emark_margin_left", readonly=False)
    emark_margin_top = fields.Integer(
        "Margin Top(em)", related="company_id.emark_margin_top", readonly=False)
    emark_img_size = fields.Integer(
        "Image Size(px)", related="company_id.emark_img_size", readonly=False)

    @api.depends('report_layout_id', 'logo', 'font', 'primary_color', 'secondary_color', 'report_header', 'report_footer', "emark_margin_left", "emark_margin_top", "emark_img_size")
    def _compute_preview(self):
        """ compute a qweb based preview to display on the wizard """

        styles = self._get_asset_style()

        for wizard in self:
            if wizard.report_layout_id:
                preview_css = self._get_css_for_preview(styles, wizard.id)
                ir_ui_view = wizard.env['ir.ui.view']
                wizard.preview = ir_ui_view._render_template('web.report_invoice_wizard_preview', {
                                                             'company': wizard, 'preview_css': preview_css})
            else:
                wizard.preview = False
