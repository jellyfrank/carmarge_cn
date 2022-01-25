#!/usr/bin/python3
# @Time    : 2022-01-25
# @Author  : Kevin Kong (kfx2007@163.com)


from odoo import api, fields, models, _


class purchase_report(models.Model):

    _inherit = "purchase.report"

    delivery_cost_line = fields.Float("运费")
    discount_manual_line = fields.Float("优惠")
    amount_tax = fields.Float("税")

    def _select(self):
        select_str = """
            WITH currency_rate as (%s)
                SELECT
                    po.id as order_id,
                    min(l.id) as id,
                    po.date_order as date_order,
                    po.state,
                    po.date_approve,
                    po.dest_address_id,
                    po.partner_id as partner_id,
                    po.user_id as user_id,
                    po.company_id as company_id,
                    po.fiscal_position_id as fiscal_position_id,
                    round(l.delivery_cost_line,2) as delivery_cost_line,
                    round(l.discount_manual_line,2) as discount_manual_line,
                    l.price_tax as amount_tax,
                    l.product_id,
                    p.product_tmpl_id,
                    t.categ_id as category_id,
                    po.currency_id,
                    t.uom_id as product_uom,
                    extract(epoch from age(po.date_approve,po.date_order))/(24*60*60)::decimal(16,2) as delay,
                    extract(epoch from age(l.date_planned,po.date_order))/(24*60*60)::decimal(16,2) as delay_pass,
                    count(*) as nbr_lines,
                    round(sum(l.price_total / COALESCE(po.currency_rate, 1.0) + l.delivery_cost_line - l.discount_manual_line)::decimal(16,2),2) as price_total,
                    (sum(l.product_qty * l.price_unit / COALESCE(po.currency_rate, 1.0))/NULLIF(sum(l.product_qty/line_uom.factor*product_uom.factor),0.0))::decimal(16,2) as price_average,
                    partner.country_id as country_id,
                    partner.commercial_partner_id as commercial_partner_id,
                    analytic_account.id as account_analytic_id,
                    sum(p.weight * l.product_qty/line_uom.factor*product_uom.factor) as weight,
                    sum(p.volume * l.product_qty/line_uom.factor*product_uom.factor) as volume,
                    sum(l.price_subtotal / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as untaxed_total,
                    sum(l.product_qty / line_uom.factor * product_uom.factor) as qty_ordered,
                    sum(l.qty_received / line_uom.factor * product_uom.factor) as qty_received,
                    sum(l.qty_invoiced / line_uom.factor * product_uom.factor) as qty_billed,
                    case when t.purchase_method = 'purchase' 
                         then sum(l.product_qty / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
                         else sum(l.qty_received / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
                    end as qty_to_be_billed
        """ % self.env['res.currency']._select_companies_rates()
        return select_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                po.company_id,
                po.user_id,
                po.partner_id,
                line_uom.factor,
                po.currency_id,
                l.price_unit,
                l.delivery_cost_line,
                l.discount_manual_line,
                l.price_tax,
                po.date_approve,
                l.date_planned,
                l.product_uom,
                po.dest_address_id,
                po.fiscal_position_id,
                l.product_id,
                p.product_tmpl_id,
                t.categ_id,
                po.date_order,
                po.state,
                line_uom.uom_type,
                line_uom.category_id,
                t.uom_id,
                t.purchase_method,
                line_uom.id,
                product_uom.factor,
                partner.country_id,
                partner.commercial_partner_id,
                analytic_account.id,
                po.id
        """
        return group_by_str
