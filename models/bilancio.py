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

    def action_compute_lines(self):
        self.ensure_one()
        # Delete existing lines to recompute
        self.line_ids.unlink()
        
        # 1. Trova le righe contabili (Consuntivo)
        # Search for move lines that:
        # - Belong to the condominium (via journal -> condominio_id)
        # - Are within the date range
        # - Are POSTED (parent_state)
        # - Have an Expense Type (account_id.expense_type_id) set
        
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

        # Create lines
        lines_vals = []
        for etype_id, amount in data.items():
            lines_vals.append((0, 0, {
                'expense_type_id': etype_id,
                'amount_actual': amount,
                'amount_budget': 0.0, # Budget to be implemented/loaded
            }))
        
        self.line_ids = lines_vals
        return True

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})


class GcondBilancioLine(models.Model):
    _name = 'gcond.bilancio.line'
    _description = 'Riga Bilancio'
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
