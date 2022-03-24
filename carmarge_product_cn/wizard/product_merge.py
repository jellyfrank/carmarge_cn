# -*-coding:utf-8-*-
# Author: YinZhaoXia
# Date: 2022-02-17

import datetime
from odoo import fields, models, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MergeProductAutomatic(models.TransientModel):
    """
        合并产品项
    """
    _name = 'product.merge.automatic.wizard'
    _description = '产品合并'

    @api.model
    def default_get(self, fields):
        res = super(MergeProductAutomatic, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if self.env.context.get('active_model') == 'product.template' and active_ids:
            if 'lines' in fields:
                res['lines'] = [(0, 0, {"product_tmpl_id": product_tmpl_id})
                                for product_tmpl_id in active_ids]
            if 'dst_product_temp_id' in fields:
                res['dst_product_temp_id'] = self._get_dst_product(
                    active_ids)[-1].id
        return res

    @api.model
    def _get_dst_product(self, partner_ids):
        # 计算第一个产品
        return self.env['product.template'].browse(partner_ids).sorted(
            key=lambda p: (
                p.active, (p.create_date or datetime.datetime(1970, 1, 1))),
            reverse=True,
        )

    dst_product_temp_id = fields.Many2one('product.template', string='目标产品')
    lines = fields.One2many(
        "product.merge.automatic.wizard.line", "order_id", string="明细")

    def action_product_merge(self):
        """ 合并产品 """
        _logger.debug(f"[产品合并]开始合并产品")
        purchases_count, sales_count, qty_available = 0, 0, 0  # 采购数量值 销售数量值 在手数量
        product_ids_list, barcode_list = [], []
        print( self.lines)
        purchase_info_ids, seller_ids = [], []
        purchase_infos = self.dst_product_temp_id.seller_ids
        if purchase_infos:
            for pi in purchase_infos:
                purchase_info_ids.append(pi.name.id)
        for line in self.lines:
            product_temp = line.product_tmpl_id
            qty_available += product_temp.qty_available
            product_ids_list.extend(product_temp.product_variant_ids.ids)
            barcode_list.append(product_temp.barcode)
            if product_temp != self.dst_product_temp_id:
                # 将归档产品的销售采购数量加总到保留产品上
                purchases_count += product_temp.purchased_product_qty
                sales_count += product_temp.sales_count
                # 将除目标产品外的产品进行归档
                product_temp.active = False

                for info in product_temp.seller_ids:
                    if info.name.id not in purchase_info_ids:
                        seller_ids.append((0,False,{
                            'name':info.name.id,
                            'price':info.price,
                            'delay':info.delay,
                            'product_id':info.product_id.id if info.product_id else False,
                            'product_name':info.product_name if info.product_code else False,
                            'product_code':info.product_code if info.product_code else False,
                            'date_start':info.date_start if info.date_start else False,
                            'date_end':info.date_end if info.date_end else False,
                            'min_qty':info.min_qty
                        }))
        # 将归档产品的采购数量加总到保留产品上
        data = {
            "other_purchases_count": purchases_count,
            "other_sales_count": sales_count,
            "merge_temp_ids": ','.join(str(p.id) for p in self.lines.product_tmpl_id),
            "seller_ids":seller_ids
        }
        # 如果目标产品有条码 就用目标产品的条码 如果没有 就选最小的那个
        if not self.dst_product_temp_id.barcode:
            data['barcode'] = sorted(barcode_list)[
                0] if barcode_list else None
        else:
            data['barcode'] = self.dst_product_temp_id.barcode
        _logger.debug(f"[产品合并]产品合并数据:{data}")
        self.dst_product_temp_id.write(data)
        # 将在手数量进行更新
        inventory_obj = self.env["stock.inventory"].create({
            'product_ids': [(6, 0, product_ids_list)],
        })
        # 复用系统原生库存盘点逻辑
        for inventory in inventory_obj:
            if inventory.state != 'draft':
                continue
            vals = {
                'state': 'confirm',
                'date': fields.Datetime.now()
            }
            if not inventory.line_ids and not inventory.start_empty:
                line_values = inventory._get_inventory_lines_values()
                if line_values:
                    # 将所有的产品进行盘点(在不修改原生逻辑的情况下)
                    for line in line_values:
                        if line['product_id'] not in self.dst_product_temp_id.product_variant_ids.ids:
                            line['product_qty'] = 0
                        else:
                            line['product_qty'] = qty_available
                else:
                    location_id = self.env['stock.location'].search([('usage','=','internal')],limit=1)
                    line_values = {
                        "inventory_id": inventory.id,
                        "product_id": self.dst_product_temp_id.product_variant_id.id,
                        "product_qty": qty_available,
                        "location_id": location_id.id,
                        "company_id": inventory.company_id.id
                    }
                    print(line_values)
                self.env['stock.inventory.line'].create(line_values)
            inventory.write(vals)
        # inventory_obj._action_start()
        inventory_obj._check_company()
        # 验证盘点
        inventory_obj.action_validate()


class MergeProductAutomaticLine(models.TransientModel):
    _name = "product.merge.automatic.wizard.line"

    order_id = fields.Many2one("product.merge.automatic.wizard")
    product_tmpl_id = fields.Many2one('product.template', string='选中的产品')
    categ_id = fields.Many2one(
        "product.category", related="product_tmpl_id.categ_id")
    name = fields.Char("name", related="product_tmpl_id.name")
    default_code = fields.Char(
        "default_code", related="product_tmpl_id.default_code")
    barcode = fields.Char("barcode", related="product_tmpl_id.barcode")
