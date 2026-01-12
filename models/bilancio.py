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
        
        for etype_id, amount in data.items():
            # A. Create Aggregated Line
            lines_vals.append((0, 0, {
                'expense_type_id': etype_id,
                'amount_actual': amount,
                'amount_budget': 0.0, 
            }))
            
            # B. Distribute Amount to Residents (Prospetto di Riparto)
            # Find the Table Master for this Expense Type and Condominio
            table_master = self.env['account.condominio.table.master'].search([
                ('condominio_id', '=', self.condominio_id.id),
                ('expense_type_id', '=', etype_id)
            ], limit=1)
            
            if table_master:
                # Distribution logic:
                # 1. Calculate Base Amount adjusted by master percentage
                base_amount = (amount * table_master.percentuale) / 100.0
                # 2. Divide by 1000 to get value per millesimal
                millesimal_base = base_amount / 1000.0
                
                for row in table_master.table_ids:
                    if not row.condomino_id:
                        continue
                    
                    # 3. Calculate Share: Base * Millesimi * Competence%
                    # Note: We do NOT apply 1.22 IVA here because 'amount' from accounting is already including tax (if gross) 
                    # or excluding tax depending on account type. Usually expenses on P&L accounts are net, 
                    # BUT condominium accounting is often 'cassa' like.
                    # HOWEVER: 'balance' in move lines is the signed amount.
                    # Assuming standard distribution logic:
                    
                    share = millesimal_base * row.value_distribution * (row.quote / 100.0)
                    
                    if share != 0:
                        riparto_vals.append((0, 0, {
                            'partner_id': row.condomino_id.id,
                            'expense_type_id': etype_id,
                            'millesimi': row.value_distribution,
                            'amount': share,
                        }))
            else:
                _logger.warning("No distribution table found for Expense Type ID %s in Condominio %s", etype_id, self.condominio_id.name)

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
                    'values': {type_id: amount, ...},
                    'total': sum(amounts)
                }, ...
            ],
            'totals_col': {type_id: sum(all_rows), ...},
            'grand_total': sum(all)
        }
        """
        self.ensure_one()
        
        # 1. Identify all used Expense Types (Columns)
        expense_types = self.riparto_ids.mapped('expense_type_id').sorted('name')
        
        # 2. Identify all Partners (Rows)
        partners = self.riparto_ids.mapped('partner_id').sorted('name')
        
        rows = []
        grand_total = 0.0
        totals_col = {et.id: 0.0 for et in expense_types}
        
        for partner in partners:
            row_vals = {}
            row_total = 0.0
            
            # Get all lines for this partner
            partner_lines = self.riparto_ids.filtered(lambda r: r.partner_id == partner)
            
            for et in expense_types:
                # Find line for this type
                line = partner_lines.filtered(lambda l: l.expense_type_id == et)
                amount = sum(line.mapped('amount')) # Should be one, but sum is safe
                row_vals[et.id] = amount
                
                # Update totals
                row_total += amount
                totals_col[et.id] += amount
            
            rows.append({
                'partner': partner,
                'values': row_vals,
                'total': row_total
            })
            grand_total += row_total
            
        return {
            'columns': expense_types,
            'rows': rows,
            'totals_col': totals_col,
            'grand_total': grand_total
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
    
    currency_id = fields.Many2one(related='bilancio_id.currency_id')
