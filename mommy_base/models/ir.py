#!/usr/bin/python3
# @Time    : 2022-10-07
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class ir_actions_actions(models.Model):
    _inherit="ir.actions.actions"

class ir_model(models.Model):
    _inherit="ir.model"

    track = fields.Boolean('Track All', help='Track all fields changes and displaying on chatter?')


class moneytray_converter(models.AbstractModel):
    _inherit = 'ir.qweb.field.monetary'

    @api.model
    def value_to_html(self, value, options):
        display_currency = options['display_currency']

        if not isinstance(value, (int, float)):
            raise ValueError(_("The value send to monetary field is not a number."))

        # lang.format mandates a sprintf-style format. These formats are non-
        # minimal (they have a default fixed precision instead), and
        # lang.format will not set one by default. currency.round will not
        # provide one either. So we need to generate a precision value
        # (integer > 0) from the currency's rounding (a float generally < 1.0).
        fmt = "%.{0}f".format(display_currency.decimal_places)

        if options.get('from_currency'):
            date = options.get('date') or fields.Date.today()
            company_id = options.get('company_id')
            if company_id:
                company = self.env['res.company'].browse(company_id)
            else:
                company = self.env.company
            value = options['from_currency']._convert(value, display_currency, company, date)

        lang = self.user_lang()
        formatted_amount = lang.format(fmt, display_currency.round(value),
                                grouping=True, monetary=True).replace(r' ', u'\N{NO-BREAK SPACE}').replace(r'-', u'-\N{ZERO WIDTH NO-BREAK SPACE}')

        pre = post = u''
        display_smybol = options.get("symbol", True)
        if display_smybol:
            if display_currency.position == 'before':
                pre = u'{symbol}\N{NO-BREAK SPACE}'.format(symbol=display_currency.symbol or '')
            else:
                post = u'\N{NO-BREAK SPACE}{symbol}'.format(symbol=display_currency.symbol or '')

        return u'{pre}<span class="oe_currency_value">{0}</span>{post}'.format(formatted_amount, pre=pre, post=post)