#!/usr/bin/python3
# @Time    : 2022-01-24
# @Author  : Kevin Kong (kfx2007@163.com)

import re

from odoo import fields, models, tools, api
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError
import logging
from dateutil.relativedelta import relativedelta
from datetime import timedelta, time
from datetime import datetime
from odoo.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)

ORIGINS = [
    ('self', '自营产品'),
    ('purchase', '外采产品')
]


class product_template(models.Model):

    _inherit = "product.template"

    @api.depends("packaging_ids")
    def _get_packaging(self):
        """"""
        for product in self:
            if not product.packaging_ids:
                product.packaging = None
            else:
                product.packaging = product.packaging_ids[0]

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

    def _compute_standard_price_update_group(self):
        self.group_use_product_standard_price_update = self.user_has_groups(
            'carmarge_product_cn.group_use_product_standard_price_update')

    @api.model
    def _default_standard_price_update(self):
        return self.user_has_groups('carmarge_product_cn.group_use_product_standard_price_update')

    @api.model
    def _search_purchase_qty(self, operator, operand):
        """搜索采购数量"""
        if operator not in ('>', '>=', '<', '<=', '='):
            return []
        if type(operand) not in (float, int):
            return []
        if operator == '=':
            operator = '=='
        records = self.search([])
        result = records.filtered(lambda record: eval(
            f"record.purchased_product_qty {operator} {operand}", locals_dict={'record': record}))
        return [('id', 'in', result.ids)]

    @api.model
    def _searhc_virtual_available(self, operator, operand):
        """搜索预测数量"""
        if operator not in ('>', '>=', '<', '<=', '='):
            return []
        if type(operand) not in (float, int):
            return []
        if operator == '=':
            operator = '=='
        records = self.search([])
        result = records.filtered(lambda record: eval(
            f"record.virtual_available {operator} {operand}", locals_dict={'record': record}))
        return [('id', 'in', result.ids)]

    @api.model
    def _search_sales_count(self, operator, operand):
        """搜索预测数量"""
        if operator not in ('>', '>=', '<', '<=', '='):
            return []
        if type(operand) not in (float, int):
            return []
        if operator == '=':
            operator = '=='
        records = self.search([])
        result = records.filtered(lambda record: eval(
            f"record.sales_count {operator} {operand}", locals_dict={'record': record}))
        return [('id', 'in', result.ids)]

    @api.depends("product_variant_id")
    def _compute_price_history(self):
        """"计算历史价格"""
        for product in self:
            lines = self.env['sale.order.line'].sudo().search(
                [('product_id', '=', product.product_variant_id.id)], limit=100)
            data = [(0, 0, {
                "sale_date": datetime.strftime(line.order_id.date_order, '%Y-%m-%d %H:%M:%S'),
                "sale_order": line.order_id.id,
                "product_uom": line.product_uom.id,
                "quantity": line.product_uom_qty,
                "currency_id": line.order_id.currency_id.id,
                "price_list": line.order_id.pricelist_id.id,
                "price": line.price_unit,
                "partner_id": line.order_id.partner_id.id,
                "product_id": line.product_id.id
            }) for line in lines]
            # data.insert(0,(5,))
            product.sale_price_history = data

    def _compute_exw_rate(self):
        """计算加价率"""
        for product in self:
            # 只考虑公开价格表
            public_pricelist = self.env.ref("product.list0") 
            product.exw_rate = sum( abs(price) for price in public_pricelist.item_ids.filtered(lambda i: i.product_tmpl_id == product).mapped("price_discount"))
            # 计算出厂价
            # product.exw = public_pricelist.get_product_price(product.product_variant_id,1,self.env.company.partner_id)
            product.exw = product.standard_price * (100 + product.exw_rate) / 100


    comm_check = fields.Boolean("商检", default=False)
    brand = fields.Many2many("product.brand", string="适用")
    exw = fields.Monetary("标准售价", compute="_compute_exw_rate")
    exw_rate = fields.Float("加价率%",compute="_compute_exw_rate")
    default_code = fields.Char(string="配件编号")
    
    height = fields.Float("高")
    is_brand_package = fields.Boolean("品牌包装")
    invoice_policy = fields.Selection(default='delivery')
    length = fields.Float("长")
    net_weight = fields.Float(string="净重")
    packaging = fields.Many2one(
        "product.packaging", string="包装", compute="_get_packaging")
    packaging_length = fields.Float("包装长(CM)", related="packaging.length")
    packaging_width = fields.Float("包装宽(CM)", related="packaging.width")
    packaging_height = fields.Float("包装高(CM)", related="packaging.height")
    packaging_volume = fields.Float(
        "包装体积(CM", related="packaging.volume", digits=(16, 4))
    packaging_net_weight = fields.Float(
        "包装净重(KG)", related="packaging.net_weight")
    packaging_weight = fields.Float("包装毛重(KG)", related="packaging.weight")
    packaging_ids = fields.One2many(string="产品包装")
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

    group_use_product_standard_price_update = fields.Boolean(string="采购成本是否可编辑", default=_default_standard_price_update,
                                                             compute="_compute_standard_price_update_group")
    purchased_product_qty = fields.Float(search=_search_purchase_qty)
    virtual_available = fields.Float(search=_searhc_virtual_available)
    sales_count = fields.Float(search=_search_sales_count)
    sale_price_history = fields.Many2many(
        "product.price.history", string="历史价格", compute="_compute_price_history")
    origin_type = fields.Selection(ORIGINS, string="产品属性", default='self')
    is_cost_service = fields.Boolean("Cost Service", default=False)

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
            if vals['type'] != 'service':
                categ_id = self._validate_category_length(categ_id)
            else:
                categ_id = self.env['product.category'].browse(categ_id)
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
            # if self.barcode:
            #     new_code = f"{code_prefix}{self.barcode[-4:]}"
            #     if new_code != self.barcode:
            #         vals['barcode'] = f"{code_prefix}{self.barcode[-4:]}"
            # else:
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

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
            继承read_group隐藏产品分组中 长、宽、高、体积、净重、毛重 汇总金额值
        """
        drops = ['length', 'width', 'height', 'volume', 'net_weight', 'weight']
        for drop in drops:
            if drop in fields:
                fields.remove(drop)

        return super(product_template, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                        orderby=orderby, lazy=lazy)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res['invoice_policy'] = 'delivery'
        return res

class product_brand(models.Model):
    _name = "product.brand"

    name = fields.Char("Product Brand")


class ProductProduct(models.Model):

    _inherit = 'product.product'

    def _compute_purchased_product_qty(self):
        date_from = fields.Datetime.to_string(
            fields.Date.context_today(self) - relativedelta(years=1))
        domain = [
            ('order_id.state', 'in', ['purchase', 'done']),
            ('product_id', 'in', self.ids),
            ('order_id.date_approve', '>=', date_from)
        ]
        order_lines = self.env['purchase.order.line'].read_group(
            domain, ['product_id', 'product_uom_qty'], ['product_id'])
        purchased_data = dict(
            [(data['product_id'][0], data['product_uom_qty']) for data in order_lines])
        for product in self:
            if not product.id:
                product.purchased_product_qty = 0.0
                continue
            product.purchased_product_qty = float_round(purchased_data.get(
                product.id, 0), precision_rounding=product.uom_id.rounding)

            if product.product_tmpl_id.other_purchases_count:
                product.purchased_product_qty = product.purchased_product_qty + \
                    product.product_tmpl_id.other_purchases_count

    def _compute_sales_count(self):
        r = {}
        self.sales_count = 0
        if not self.user_has_groups('sales_team.group_sale_salesman'):
            return r
        date_from = fields.Datetime.to_string(fields.datetime.combine(fields.datetime.now() - timedelta(days=365),
                                                                      time.min))

        done_states = self.env['sale.report']._get_done_states()

        domain = [
            ('state', 'in', done_states),
            ('product_id', 'in', self.ids),
            ('date', '>=', date_from),
        ]
        for group in self.env['sale.report'].read_group(domain, ['product_id', 'product_uom_qty'], ['product_id']):
            r[group['product_id'][0]] = group['product_uom_qty']
        sales_count = 0
        for product in self:
            if not product.id:
                product.sales_count = 0.0
                continue
            sales_count = float_round(
                r.get(product.id, 0), precision_rounding=product.uom_id.rounding)
            if product.product_tmpl_id.other_sales_count:
                product.sales_count = sales_count + product.product_tmpl_id.other_sales_count
            else:
                product.sales_count = sales_count

        return r
