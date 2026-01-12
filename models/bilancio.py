# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class GcondBilancio(models.Model):
    _name = 'gcond.bilancio'
    _description = 'Bilancio Condominiale'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Descrizione', required=True, tracking=True)
    condominio_id = fields.Many2one('account.condominio', string='Condominio', required=True, tracking=True)
    date_start = fields.Date(string='Data Inizio', required=True, tracking=True)
    date_end = fields.Date(string='Data Fine', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Bozza'),
        ('approved', 'Approvato'),
        ('closed', 'Chiuso')
    ], string='Stato', default='draft', tracking=True)
    
    # Currency usually comes from company or account.journal
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, readonly=True)

    line_ids = fields.One2many('gcond.bilancio.line', 'bilancio_id', string='Righe Bilancio')
    riparto_ids = fields.One2many('gcond.bilancio.riparto', 'bilancio_id', string='Ripartizione per Condomino')

    def action_compute_lines(self):
        self.ensure_one()
        # Delete existing lines to recompute
        self.line_ids.unlink()
        self.riparto_ids.unlink()
        
        # 1. Trova le righe contabili (Consuntivo)
        domain = [
            ('move_id.journal_id.condominio_id', '=', self.condominio_id.id),
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
            ('parent_state', '=', 'posted'),
            ('account_id.expense_type_id', '!=', False),
        ]
        
        amls = self.env['account.move.line'].search(domain)
        _logger.info("GCOND Bilancio: Found %s move lines for consuntivo", len(amls))
        
        # Group by Expense Type
        data = {}
        for line in amls:
            etype = line.account_id.expense_type_id
            if etype.id not in data:
                data[etype.id] = 0.0
            
            # Balance = Debit - Credit. For Expenses (Debit), this is positive.
            data[etype.id] += line.balance

        # Create lines (Aggregated)
        lines_vals = []
        riparto_vals = []
        
        # Pre-fetch financial data per partner
        # We need to find all partners involved in this condominio.
        # But partners are defined in the distribution tables...
        # So we can calculate financials "on demand" inside the loop? 
        # No, better to calculate once per partner to avoid repetitive DB calls.
        
        # Strategy:
        # 1. Collect all partners from table masters used for these expense types.
        # 2. For each partner, calc Payments and Previous Balance.
        # 3. Store in a dict {partner_id: {'payments': X, 'previous': Y}}
        
        partner_financials = {}
        
        def get_partner_financials(partner_id):
            if partner_id in partner_financials:
                return partner_financials[partner_id]
            
            # Calc Payments: Sum of Credit lines in Journal(s) linked to Condominio?
            # Or dedicated accounts? 
            # Logic: Payments are credits on Receivable account (121001 etc).
            # The resident pays -> Bank Debit, Partner Credit.
            # So search for credits on partner account.
            
            domain_pay = [
                ('partner_id', '=', partner_id),
                ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
                ('parent_state', '=', 'posted'),
                ('date', '>=', self.date_start),
                ('date', '<=', self.date_end),
                ('credit', '>', 0) # Only payments
            ]
            # Restrict to journals of this condominio? 
            # Usually yes, but if partner pays via Bank general journal?
            # Let's restrict to move lines where move.journal_id has condominio_id = self.condominio_id
            # Wait, `account.move.line` doesn't have `condominio_id` directly but via `journal_id`.
            domain_pay.append(('move_id.journal_id.condominio_id', '=', self.condominio_id.id))
            
            pay_lines = self.env['account.move.line'].search(domain_pay)
            payments = sum(pay_lines.mapped('credit'))
            
            # Calc Previous: Balance at date_start - 1 day
            # Balance = Debit - Credit
            domain_prev = [
                ('partner_id', '=', partner_id),
                ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
                ('parent_state', '=', 'posted'),
                ('date', '<', self.date_start),
                ('move_id.journal_id.condominio_id', '=', self.condominio_id.id)
            ]
            prev_lines = self.env['account.move.line'].search(domain_prev)
            previous = sum(prev_lines.mapped('balance'))
            
            res = {'payments': payments, 'previous': previous}
            partner_financials[partner_id] = res
            return res

        for etype_id, amount in data.items():
            # A. Create Aggregated Line
            lines_vals.append((0, 0, {
                'expense_type_id': etype_id,
                'amount_actual': amount,
                'amount_budget': 0.0, 
            }))
            
            # B. Distribute Amount to Residents
            table_master = self.env['account.condominio.table.master'].search([
                ('condominio_id', '=', self.condominio_id.id),
                ('expense_type_id', '=', etype_id)
            ], limit=1)
            
            if table_master:
                base_amount = (amount * table_master.percentuale) / 100.0
                millesimal_base = base_amount / 1000.0
                
                for row in table_master.table_ids:
                    if not row.condomino_id:
                        continue
                    
                    share = millesimal_base * row.value_distribution * (row.quote / 100.0)
                    
                    if share != 0:
                        fin = get_partner_financials(row.condomino_id.id)
                        
                        riparto_vals.append((0, 0, {
                            'partner_id': row.condomino_id.id,
                            'expense_type_id': etype_id,
                            'millesimi': row.value_distribution,
                            'amount': share,
                            'payments': fin['payments'],
                            'previous_balance': fin['previous']
                        }))
            else:
                _logger.warning("No distribution table found for Expense Type ID %s", etype_id)

        self.line_ids = lines_vals
        self.riparto_ids = riparto_vals
        return True

    def get_riparto_matrix(self):
        """
        Returns a dictionary suitable for QWeb report:
        {
            'columns': [obj(gcond.expense.type), ...],
            'rows': [
                {
                    'partner': obj(res.partner),
                    'values': {type_id: (millesimi, amount), ...},
                    'total_quota': float,
                    'payments': float,
                    'previous': float,
                    'balance': float
                }, ...
            ],
            'totals_col': {type_id: sum(all_rows), ...},
            'grand_total_quota': float,
            'grand_total_payments': float,
            'grand_total_previous': float,
            'grand_total_balance': float
        }
        """
        self.ensure_one()
        
        # 1. Identify all used Expense Types (Columns)
        expense_types = self.riparto_ids.mapped('expense_type_id').sorted('name')
        
        # 2. Identify all Partners (Rows)
        partners = self.riparto_ids.mapped('partner_id').sorted('name')
        
        rows = []
        grand_total_quota = 0.0
        grand_total_payments = 0.0
        grand_total_previous = 0.0
        grand_total_balance = 0.0
        
        totals_col = {et.id: 0.0 for et in expense_types}
        
        for partner in partners:
            row_vals = {}
            row_quota = 0.0
            
            # Get all lines for this partner
            partner_lines = self.riparto_ids.filtered(lambda r: r.partner_id == partner)
            
            # Data from the first line found (since payments/previous are repeated per partner in DB logic or should be calculated once)
            # Actually, my DB design duplicates this info per expense type row? 
            # ideally gcond.bilancio.riparto has one row per (partner, expense_type).
            # So I need to aggregate.
            
            # Use the first line to get partner-level financials (calculated during compute)
            # Wait, I haven't implemented compute logic for payments yet.
            # I should do that first.
            
            # Let's pivot data
            for et in expense_types:
                line = partner_lines.filtered(lambda l: l.expense_type_id == et)
                amount = sum(line.mapped('amount'))
                millesimi = sum(line.mapped('millesimi'))
                row_vals[et.id] = (millesimi, amount)
                
                row_quota += amount
                totals_col[et.id] += amount
            
            # Get financial info (Unified per partner)
            # Since I will store payments/previous on every riparto line, I can just take the first one or average?
            # Better: The new model structure should probably be:
            # - gcond.bilancio.riparto: (partner, expense_type, millesimi, amount) -> Detail
            # - gcond.bilancio.partner_summary: (partner, payments, previous, final) -> Summary
            # But the user asked for one big table.
            # I'll stick to 'gcond.bilancio.riparto' having these fields computed. 
            # I will ensure they are identical for all rows of the same partner.
            
            first_line = partner_lines[0] if partner_lines else None
            payments = first_line.payments if first_line else 0.0
            previous = first_line.previous_balance if first_line else 0.0
            # Recompute balance in case items are filtered? No, reliance on DB.
            balance = row_quota - payments + previous
            
            rows.append({
                'partner': partner,
                'values': row_vals,
                'total_quota': row_quota,
                'payments': payments,
                'previous': previous,
                'balance': balance
            })
            
            grand_total_quota += row_quota
            grand_total_payments += payments
            grand_total_previous += previous
            grand_total_balance += balance
            
        return {
            'columns': expense_types,
            'rows': rows,
            'totals_col': totals_col,
            'grand_total_quota': grand_total_quota,
            'grand_total_payments': grand_total_payments,
            'grand_total_previous': grand_total_previous,
            'grand_total_balance': grand_total_balance
        }
    
    def action_print_bilancio(self):
        return self.env.ref('gcond.action_report_bilancio').report_action(self)

    def action_print_riparto(self):
        return self.env.ref('gcond.action_report_riparto').report_action(self)

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})


class GcondBilancioLine(models.Model):
    _name = 'gcond.bilancio.line'
    _description = 'Riga Bilancio Aggregata'
    _order = 'expense_type_id'

    bilancio_id = fields.Many2one('gcond.bilancio', string='Bilancio', required=True, ondelete='cascade')
    expense_type_id = fields.Many2one('gcond.expense.type', string='Tipo Spesa', required=True)
    
    amount_budget = fields.Monetary(string='Preventivo', currency_field='currency_id')
    amount_actual = fields.Monetary(string='Consuntivo', currency_field='currency_id')
    difference = fields.Monetary(string='Differenza', compute='_compute_difference', currency_field='currency_id')
    
    currency_id = fields.Many2one(related='bilancio_id.currency_id')

    @api.depends('amount_budget', 'amount_actual')
    def _compute_difference(self):
        for line in self:
            line.difference = line.amount_budget - line.amount_actual


class GcondBilancioRiparto(models.Model):
    _name = 'gcond.bilancio.riparto'
    _description = 'Dettaglio Riparto Spese'
    _order = 'partner_id, expense_type_id'

    bilancio_id = fields.Many2one('gcond.bilancio', string='Bilancio', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Condomino', required=True)
    expense_type_id = fields.Many2one('gcond.expense.type', string='Tipo Spesa', required=True)
    
    millesimi = fields.Float(string='Millesimi')
    amount = fields.Monetary(string='Quota Ripartita', currency_field='currency_id')
    
    # Financials (Repeated for every row of the same partner to make view easier)
    payments = fields.Monetary(string='Versato', currency_field='currency_id')
    previous_balance = fields.Monetary(string='Pregresso', currency_field='currency_id')
    final_balance = fields.Monetary(string='Conguaglio', compute='_compute_final_balance', currency_field='currency_id')
    
    currency_id = fields.Many2one(related='bilancio_id.currency_id')
    
    @api.depends('amount', 'payments', 'previous_balance')
    def _compute_final_balance(self):
        # NOTE: This compute is per row, which represents a single expense type share.
        # But 'payments' and 'previous_balance' are totals for the partner.
        # So 'final_balance' here is meaningless if summed? 
        # Correct approach: logic should be handled at report level or summary level.
        # But to show it in the tree view, we might need a workaround.
        # actually, the user wants the final matrix.
        # Let's keep these fields as data holders. 
        # The 'final_balance' on the row is confusing.
        # It's better to NOT compute it per row, but maybe make it 0 for all rows 
        # except a 'dummy' row? No.
        # Let's just remove the compute and fill it during generation?
        # Or keeping it simple: The report logic handles the math. 
        # The Tree view is just a list.
        for line in self:
             line.final_balance = 0.0 # Placeholder
