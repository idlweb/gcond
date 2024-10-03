from odoo import models, fields, api
from odoo.exceptions import UserError
from decimal import Decimal

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement.line'

    amount_consumed = fields.Boolean(string='Importo Consumato', default=False)

    def action_consume_payment(self):
        for statement in self:
            if not statement.line_ids:
                continue

            importo = statement.amount #+ self.get_previous_residual(statement.line_ids[0].partner_id.id)         
            partner = statement.line_ids[0].partner_id
            if not partner:
                raise UserError("Nessun partner associato a questa riga dell'estratto conto.")

            unpaid_lines = self.env['account.move.line'].search([
                ('account_id', '=', partner.conto_id.id),
                ('move_id.payment_state', '!=', 'paid')
            ])

            somma_quote = self.somma_quote_da_pagare(partner.conto_id.id)

            for unpaid_line in unpaid_lines:
                if importo >= unpaid_line.debit:
                    unpaid_line.move_id.payment_state = 'paid'
                    importo -= unpaid_line.debit
                else:
                    if importo > 0:
                        statement.amount_residual = importo #Decimal(importo).quantize(Decimal('0.01'))
                    break
           
            statement.amount_consumed = True

            """
            # Crea una scrittura contabile
            move_vals = {
                'journal_id': statement.journal_id.id,
                'date': fields.Date.context_today(self),
                'line_ids': [
                    (0, 0, {
                        'account_id': partner.property_account_receivable_id.id,
                        'partner_id': partner.id,
                        'credit': statement.amount,
                        'debit': 0,
                    }),
                    (0, 0, {
                        'account_id': self.env['account.account'].search([('name', 'ilike', partner.name)], limit=1).id,
                        'partner_id': partner.id,
                        'credit': 0,
                        'debit': statement.amount,
                    }),
                ],
            }
            self.env['account.move'].create(move_vals)
            """

    def get_previous_residual(self, partner_id):
        previous_statements = self.env['account.bank.statement.line'].search([
            ('partner_id', '=', partner_id),
            ('amount_consumed', '=', True)
        ], order='date desc', limit=1)

        if previous_statements:
            residual = previous_statements.amount_residual
            previous_statements.amount_residual = 0
            return residual
        
        return 0


    def somma_quote_da_pagare(self, account_id):
        result = self.env['account.move.line'].read_group(
            domain=[
                ('account_id', '=', account_id),
                ('move_id.payment_state', '!=', 'paid')
            ],
            fields=['debit:sum'],
            groupby=[]
        )
        return result[0]['debit'] if result else 0