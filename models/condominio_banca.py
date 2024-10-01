from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement.line'

    amount_consumed = fields.Boolean(string='Importo Consumato', default=False)

    def action_consume_payment(self):
        for statement in self:
            if not statement.line_ids:
                continue

            importo = statement.amount + statement.amount_residual
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
                        statement.amount_residual = round(importo, 2)
                    break

            statement.amount_consumed = True

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