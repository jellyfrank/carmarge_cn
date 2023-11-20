#!/usr/bin/python3
# @Time    : 2022-05-20
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class account_move(models.Model):
    _inherit="account.move"
    
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        "delivery_cost",
        "discount_manual")
    def _compute_amount(self):
        for move in self:
            if move.payment_state == 'invoicing_legacy':
                # invoicing_legacy state is set via SQL when setting setting field
                # invoicing_switch_threshold (defined in account_accountant).
                # The only way of going out of this state is through this setting,
                # so we don't recompute it here.
                move.payment_state = move.payment_state
                continue

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = move._get_lines_onchange_currency().currency_id

            for line in move.line_ids:
                if move.is_invoice(include_receipts=True):
                    # === Invoices ===
                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_to_pay += line.balance
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies or move.company_id.currency_id

            # Compute 'payment_state'.
            new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

            if move.is_invoice(include_receipts=True) and move.state == 'posted':

                if currency.is_zero(move.amount_residual):
                    reconciled_payments = move._get_reconciled_payments()
                    if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                        new_pmt_state = 'paid'
                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    new_pmt_state = 'partial'

            if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
                reverse_moves = self.env['account.move'].search([('reversed_entry_id', '=', move.id), ('state', '=', 'posted'), ('move_type', '=', reverse_type)])

                # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                    new_pmt_state = 'reversed'

            move.payment_state = new_pmt_state

            # 排除海运费和优惠
            move.amount_untaxed -= (move.delivery_cost + move.discount_manual)
            move.amount_total = move.amount_untaxed +move.amount_tax + move.delivery_cost + move.discount_manual
            # move.amount_residual -= 2* move.discount_manual


    #     # for move in self:
    #     #     # if move.move_type == "in_invoice":
    #     #     # 减掉明细行多算的 运费和优惠
    #     #     # move.amount_total = move.amount_total - move.delivery_cost - move.discount_manual
    #     #     # move.amount_total = move.amount_total + move.delivery_cost - move.discount_manual
    #     #     # move.amount_residual -= (move.delivery_cost + move.discount_manual)
    #     #     # move.· = move.amount_total
    #     #     print('&&&&&&&&')
    #     #     print(move.amount_residual)

    @api.depends("invoice_line_ids.product_id", "invoice_line_ids.price_unit")
    def _compute_delivery_discount(self):
        """计算海运费和优惠"""
        delivery_product_id = self.env.ref(
            "carmarge_purchase_cn.service_delivery_cost")
        discount_product_id = self.env.ref(
            "carmarge_purchase_cn.service_discount")
        if not delivery_product_id:
            self.delivery_cost = 0
        if not discount_product_id:
            self.discount_manual = 0

        if delivery_product_id.product_variant_id in self.invoice_line_ids.product_id:
            delivery_line = self.invoice_line_ids.filtered(
                lambda l: l.product_id == delivery_product_id.product_variant_id)
            self.delivery_cost = delivery_line.price_subtotal
        else:
            self.delivery_cost = 0

        if not discount_product_id.product_variant_id in self.invoice_line_ids.product_id:
            self.discount_manual = 0

        price_subtotals  = self.invoice_line_ids.filtered(
            lambda l: l.product_id == discount_product_id.product_variant_id).mapped("price_subtotal")
        self.discount_manual = price_subtotals[0] if price_subtotals else 0

    def _recompute_payment_terms_lines(self):
        ''' Compute the dynamic payment term lines of the journal entry.'''
        self.ensure_one()
        self = self.with_company(self.company_id)
        in_draft_mode = self != self._origin
        today = fields.Date.context_today(self)
        self = self.with_company(self.journal_id.company_id)

        def _get_payment_terms_computation_date(self):
            ''' Get the date from invoice that will be used to compute the payment terms.
            :param self:    The current account.move record.
            :return:        A datetime.date object.
            '''
            if self.invoice_payment_term_id:
                return self.invoice_date or today
            else:
                return self.invoice_date_due or self.invoice_date or today

        def _get_payment_terms_account(self, payment_terms_lines):
            ''' Get the account from invoice that will be set as receivable / payable account.
            :param self:                    The current account.move record.
            :param payment_terms_lines:     The current payment terms lines.
            :return:                        An account.account record.
            '''
            if payment_terms_lines:
                # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
                return payment_terms_lines[0].account_id
            elif self.partner_id:
                # Retrieve account from partner.
                if self.is_sale_document(include_receipts=True):
                    return self.partner_id.property_account_receivable_id
                else:
                    return self.partner_id.property_account_payable_id
            else:
                # Search new account.
                domain = [
                    ('company_id', '=', self.company_id.id),
                    ('internal_type', '=', 'receivable' if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
                ]
                return self.env['account.account'].search(domain, limit=1)

        def _compute_payment_terms(self, date, total_balance, total_amount_currency):
            ''' Compute the payment terms.
            :param self:                    The current account.move record.
            :param date:                    The date computed by '_get_payment_terms_computation_date'.
            :param total_balance:           The invoice's total in company's currency.
            :param total_amount_currency:   The invoice's total in invoice's currency.
            :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
            '''
            if self.invoice_payment_term_id:
                to_compute = self.invoice_payment_term_id.compute(total_balance, date_ref=date, currency=self.company_id.currency_id)
                if self.currency_id == self.company_id.currency_id:
                    # Single-currency.
                    return [(b[0], b[1], b[1]) for b in to_compute]
                else:
                    # Multi-currencies.
                    to_compute_currency = self.invoice_payment_term_id.compute(total_amount_currency, date_ref=date, currency=self.currency_id)
                    return [(b[0], b[1], ac[1]) for b, ac in zip(to_compute, to_compute_currency)]
            else:
                return [(fields.Date.to_string(date), total_balance, total_amount_currency)]

        def _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute):
            ''' Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
            :param self:                    The current account.move record.
            :param existing_terms_lines:    The current payment terms lines.
            :param account:                 The account.account record returned by '_get_payment_terms_account'.
            :param to_compute:              The list returned by '_compute_payment_terms'.
            '''
            # As we try to update existing lines, sort them by due date.
            existing_terms_lines = existing_terms_lines.sorted(lambda line: line.date_maturity or today)
            existing_terms_lines_index = 0

            # Recompute amls: update existing line or create new one for each payment term.
            new_terms_lines = self.env['account.move.line']
            for date_maturity, balance, amount_currency in to_compute:
                currency = self.journal_id.company_id.currency_id
                if currency and currency.is_zero(balance) and len(to_compute) > 1:
                    continue

                if existing_terms_lines_index < len(existing_terms_lines):
                    # Update existing line.
                    candidate = existing_terms_lines[existing_terms_lines_index]
                    existing_terms_lines_index += 1
                    candidate.update({
                        'date_maturity': date_maturity,
                        'amount_currency': -amount_currency,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                    })
                else:
                    # Create new line.
                    create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                    candidate = create_method({
                        'name': self.payment_reference or '',
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'quantity': 1.0,
                        'amount_currency': -amount_currency,
                        'date_maturity': date_maturity,
                        'move_id': self.id,
                        'currency_id': self.currency_id.id,
                        'account_id': account.id,
                        'partner_id': self.commercial_partner_id.id,
                        'exclude_from_invoice_tab': True,
                    })

                new_terms_lines += candidate
                if in_draft_mode:
                    candidate.update(candidate._get_fields_onchange_balance(force_computation=True))
            return new_terms_lines

        existing_terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        others_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
        company_currency_id = (self.company_id or self.env.company).currency_id
        total_balance = sum(others_lines.mapped(lambda l: company_currency_id.round(l.balance)))
        total_amount_currency = sum(others_lines.mapped('amount_currency'))
    
        # 处理余额不对的问题
        # for line in others_lines:
        #     if line._is_discount():
                # debit,credit = line.debit, line.credit
                # line.debit, line.credit = line.credit, line.debit
                # total_amount_currency -= line.amount_currency * 2
                # total_balance -= line.amount_currency * 2


        
        if not others_lines:
            self.line_ids -= existing_terms_lines
            return

        computation_date = _get_payment_terms_computation_date(self)
        account = _get_payment_terms_account(self, existing_terms_lines)
        to_compute = _compute_payment_terms(self, computation_date, total_balance, total_amount_currency)
        new_terms_lines = _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute)

        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines

        if new_terms_lines:
            self.payment_reference = new_terms_lines[-1].name or ''
            self.invoice_date_due = new_terms_lines[-1].date_maturity


    delivery_cost = fields.Monetary("运费", compute="_compute_delivery_discount",store=True)
    discount_manual = fields.Monetary("优惠",compute="_compute_delivery_discount",store=True)

class account_move_line(models.Model):
    _inherit = "account.move.line"

    def _is_discount(self):
        """"""
        return self.product_id == self.env.ref("carmarge_sale_cn.service_discount").product_variant_id

    def _is_deliver_or_discount(self):
        delivery_product_id = self.env.ref(
                "carmarge_sale_cn.service_delivery_cost")
        discount_product_id = self.env.ref(
            "carmarge_sale_cn.service_discount")
        if self.product_id in [delivery_product_id.product_variant_id, discount_product_id.product_variant_id]:
            return True
        return False


    # @api.depends('debit', 'credit')
    # def _compute_balance(self):
    #     for line in self:
    #         print('************%%%%%%**************')
    #         if line._is_deliver_or_discount():
    #             print('=======0=========')
    #             line.debit = 0
    #             line.credit = 0
    #             line.balance = 0
    #         else:
    #             line.balance = line.debit - line.credit

    # @api.depends('debit', 'credit', 'amount_currency', 'account_id', 'currency_id', 'move_id.state', 'company_id',
    #              'matched_debit_ids', 'matched_credit_ids')
    # def _compute_amount_residual(self):
    #     """ Computes the residual amount of a move line from a reconcilable account in the company currency and the line's currency.
    #         This amount will be 0 for fully reconciled lines or lines from a non-reconcilable account, the original line amount
    #         for unreconciled lines, and something in-between for partially reconciled lines.
    #     """
    #     for line in self:
    #         if line.id and (line.account_id.reconcile or line.account_id.internal_type == 'liquidity'):
    #             reconciled_balance = sum(line.matched_credit_ids.mapped('amount')) \
    #                                  - sum(line.matched_debit_ids.mapped('amount'))
    #             reconciled_amount_currency = sum(line.matched_credit_ids.mapped('debit_amount_currency'))\
    #                                          - sum(line.matched_debit_ids.mapped('credit_amount_currency'))

    #             line.amount_residual = line.balance - reconciled_balance

    #             if line.currency_id:
    #                 line.amount_residual_currency = line.amount_currency - reconciled_amount_currency
    #             else:
    #                 line.amount_residual_currency = 0.0

    #             line.reconciled = line.company_currency_id.is_zero(line.amount_residual) \
    #                               and (not line.currency_id or line.currency_id.is_zero(line.amount_residual_currency))
    #         else:
    #             # Must not have any reconciliation since the line is not eligible for that.
    #             line.amount_residual = 0.0
    #             line.amount_residual_currency = 0.0
    #             line.reconciled = False