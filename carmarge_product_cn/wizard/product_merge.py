# -*-coding:utf-8-*-
# Author: YinZhaoXia
# Date: 2022-02-17

import datetime

from odoo import fields, models, api


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
            if 'product_temp_ids' in fields:
                res['product_temp_ids'] = [(6, 0, active_ids)]
            if 'dst_product_temp_id' in fields:
                res['dst_product_temp_id'] = self._get_dst_product(active_ids)[-1].id
        return res

    @api.model
    def _get_dst_product(self, partner_ids):
        # 计算第一个产品
        return self.env['product.template'].browse(partner_ids).sorted(
            key=lambda p: (p.active, (p.create_date or datetime.datetime(1970, 1, 1))),
            reverse=True,
        )

    product_temp_ids = fields.Many2many('product.template', string='选中的产品')
    dst_product_temp_id = fields.Many2one('product.template', string='目标产品')

    def action_product_merge(self):
        """ 合并产品 """
        purchases_count,sales_count, qty_available = 0, 0, 0 # 采购数量值 销售数量值 在手数量
        product_ids_list,barcode_list = [],[]
        for product_temp in self.product_temp_ids:
            qty_available += product_temp.qty_available
            product_ids_list.extend(product_temp.product_variant_ids.ids)
            barcode_list.append(product_temp.barcode)
            if product_temp != self.dst_product_temp_id:
                # 将归档产品的销售采购数量加总到保留产品上
                purchases_count += product_temp.purchased_product_qty
                sales_count += product_temp.sales_count
                # 将除目标产品外的产品进行归档
                product_temp.active = False
        # 将归档产品的采购数量加总到保留产品上
        data = {
            "other_purchases_count": purchases_count,
            "other_sales_count": sales_count,
            "merge_temp_ids": ','.join(list(map(lambda val: str(val), self.product_temp_ids.ids))),
        }
        # 如果目标产品有条码 就用目标产品的条码 如果没有 就选最小的那个
        if not self.dst_product_temp_id.barcode:
            data['barcode'] = sorted(barcode_list)[0] if barcode_list else None
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
                # 将所有的产品进行盘点(在不修改原生逻辑的情况下)
                for line in line_values:
                    if line['product_id'] not in self.dst_product_temp_id.product_variant_ids.ids:
                        line['product_qty'] = 0
                    else:
                        line['product_qty'] = qty_available
                self.env['stock.inventory.line'].create(line_values)
            inventory.write(vals)
        inventory_obj._check_company()
        # 验证盘点
        inventory_obj.action_validate()
