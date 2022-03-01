#!/usr/bin/python3
# @Time    : 2022-01-24
# @Author  : Kevin Kong (kfx2007@163.com)

import re

from odoo import fields, models, tools, api
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError
import logging 

_logger = logging.getLogger(__name__)


class product_template(models.Model):

    _inherit = "product.template"

    def _get_packaging(self):
        """"""
        for product in self:
            if not product.packaging_ids:
                product.packaging = None
            else:
                product.packaging = product.packaging_ids[0] if product.packaging_ids else None

    def _product_category_code(self, categ_id):
        # 产品类别编码汇总
        pattern = re.compile(r'^\d+')  # 是否有更漂亮的写法
        re_obj = pattern.findall(categ_id.name) if categ_id.name else ''
        category_code = re_obj[0] if re_obj else ''
        if categ_id.parent_id:
            return f"{self._product_category_code(categ_id.parent_id)}{category_code}"
        else:
            return category_code

    def _update_barcode(self, categ_id):
        return f"CA{self._product_category_code(categ_id)}"

    @tools.ormcache()
    def _get_default_uom_id(self):
        return self.env.ref('carmarge_product_cn.product_uom_number')

    def _compute_purchased_product_qty(self):
        for template in self:
            template.purchased_product_qty = float_round(
                sum([p.purchased_product_qty for p in template.product_variant_ids]),
                precision_rounding=template.uom_id.rounding)
            if template.other_purchases_count:
                template.purchased_product_qty = template.purchased_product_qty + \
                    template.other_purchases_count

    @api.depends('product_variant_ids.sales_count')
    def _compute_sales_count(self):
        for product in self:
            product.sales_count = float_round(
                sum([p.sales_count for p in product.with_context(
                    active_test=False).product_variant_ids]),
                precision_rounding=product.uom_id.rounding)

            if product.other_sales_count:
                product.sales_count = product.sales_count + product.other_sales_count

    def _check_barcode_is_active(self, code_prefix):
        """ 添加 barcode 校验"""
        barcode = f"{code_prefix}{self.env['ir.sequence'].next_by_code('product.template.barcode')}"
        # 用sql查询比较快
        self.env.cr.execute(f"""
                        SELECT id FROM product_product WHERE barcode='{barcode}'
                    """)
        res_obj = self.env.cr.fetchall()
        if res_obj:
            self._check_barcode_is_active(barcode)
        else:
            return barcode

    def _validate_category_length(self, categ_id):
        """category length must longer than 2."""
        categ_id = self.env['product.category'].browse(categ_id)
        if not categ_id.parent_id:
            raise UserError("产品分类必须精确到小类")
        return categ_id

    @api.model
    def _get_categ_next_sequence(self, prefix):
        """get next sequence under the prefix"""
        res = self.env['product.template'].search_read(
            [('barcode', '=ilike', f'{prefix}%')], ['barcode'],)
        if not res:
            return f"{prefix}{1:04}"
        else:
            barcodes = [item['barcode'] for item in res if item['barcode']]
            barcode = max(barcodes) if barcodes else None
            if not barcode:
                return f"{prefix}{1:04}"
            number = barcode.split(prefix)[1]
            if not number:
                return f"{prefix}{1:04}"
            try:
                number = int(number)
            except Exception as err:
                return f"{prefix}{1:04}"
            return f"{prefix}{number+1:04}"

    brand = fields.Many2many("product.brand", string="适用")
    comm_check = fields.Boolean("是否商检", default=False)
    default_code = fields.Char(string="配件编号")
    height = fields.Float("高")
    is_brand_package = fields.Boolean("是否品牌包装")
    length = fields.Float("长")
    net_weight = fields.Float(string="净重")
    packaging = fields.Many2one(
        "product.packaging", string="包装", compute="_get_packaging")
    packaging_length = fields.Float("包装长", related="packaging.length")
    packaging_width = fields.Float("包装宽", related="packaging.width")
    packaging_height = fields.Float("包装高", related="packaging.height")
    packaging_volume = fields.Float("包装体积", related="packaging.volume")
    packaging_net_weight = fields.Float("包装净重", related="packaging.net_weight")
    packaging_weight = fields.Float("包装毛重", related="packaging.weight")
    width = fields.Float("宽")
    weight = fields.Float(string="毛重")
    type = fields.Selection(default="product")
    translate_name = fields.Char(string="英文名称")
    uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        default=_get_default_uom_id, required=True,
        help="Default unit of measure used for all stock operations.")
    uom_po_id = fields.Many2one(
        'uom.uom', 'Purchase Unit of Measure',
        default=_get_default_uom_id, required=True,
        help="Default unit of measure used for purchase orders. It must be in the same category as the default unit of measure.")
    other_purchases_count = fields.Float(string="其他采购数量", help="当当前产品存在合并产品时")
    other_sales_count = fields.Float(string="其他销售数量", help="当当前产品存在合并产品时")
    merge_temp_ids = fields.Char(string="被合并产品IDS")

    def action_view_sales(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sale.report_all_channels_sales_action")
        # 增添被合并商品id
        is_merge = list(map(lambda value: int(value),
                            self.merge_temp_ids.split(','))) if self.merge_temp_ids else []
        action['domain'] = [
            ('product_tmpl_id', 'in', is_merge if is_merge else self.ids)]
        action['context'] = {
            'pivot_measures': ['product_uom_qty'],
            'active_id': self._context.get('active_id'),
            'active_model': 'sale.report',
            'search_default_Sales': 1,
            'time_ranges': {'field': 'date', 'range': 'last_365_days'}
        }
        return action

    def action_view_po(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "purchase.action_purchase_order_report_all")
        # 增添被合并商品id
        is_merge = list(map(lambda value: int(value),
                            self.merge_temp_ids.split(','))) if self.merge_temp_ids else []
        action['domain'] = ['&', ('state', 'in', ['purchase', 'done']),
                            ('product_tmpl_id', 'in', is_merge if is_merge else self.ids)]
        action['context'] = {
            'graph_measure': 'qty_ordered',
            'search_default_later_than_a_year_ago': True
        }
        return action

    @api.model
    def create(self, vals):
        if not vals.get('barcode'):
            categ_id = vals.get('categ_id')
            categ_id = self._validate_category_length(categ_id)
            code_prefix = self._update_barcode(categ_id)
            # vals['barcode'] = f"{code_prefix}{self.env['ir.sequence'].next_by_code('product.template.barcode')}"
            vals['barcode'] = self._get_categ_next_sequence(code_prefix)
        return super(product_template, self).create(vals)

    def write(self, vals):
        categ_id = vals.get('categ_id')
        barcode = vals.get("barcode")
        if categ_id and not barcode:
            categ_id = self._validate_category_length(categ_id)
            code_prefix = self._update_barcode(categ_id)
            if self.barcode:
                new_code = f"{code_prefix}{self.barcode[-4:]}"
                if new_code != self.barcode:
                    vals['barcode'] = f"{code_prefix}{self.barcode[-4:]}"
            else:
                # vals['barcode'] = f"{code_prefix}{self.env['ir.sequence'].next_by_code('product.template.barcode')}"
                vals['barcode'] = self._get_categ_next_sequence(code_prefix)
        return super(product_template, self).write(vals)

    def action_barcode_onclick_update(self):
        """ 一键更新历史产品数据条码值 """
        # 将product.template.barcode设置为从0开始进行计值
        # sequence_obj = self.env['ir.sequence'].search(
        #     [('code', '=', 'product.template.barcode'), ('active', '=', True)], limit=1)
        # sequence_obj.write({
        #     "number_next_actual": 1
        # })
        # 将所有的条码进行更新
        try:
            products = self.with_context(active_test=False).search([])
            products.update({'barcode': False})
            products = self.search([])
            products.barcode = False
            self.env.cr.commit()
            for product in products:
                # 因为 ”一个条形码只能分配给一个产品！“ 的_sql_constraints限制，所以添加barcode校验
                # 只针对二级分类进行重置
                if not product.categ_id.parent_id:
                    continue
                code_prefix = self._update_barcode(product.categ_id)
                barcode = self._get_categ_next_sequence(code_prefix)
                if barcode:
                    product.update({
                        "barcode": barcode
                    })
        except Exception as err:
            _logger.exception("update error")


class product_brand(models.Model):
    _name = "product.brand"

    name = fields.Char("Product Brand")
