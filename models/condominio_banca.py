from odoo import models, fields, api
from odoo.exceptions import UserError
from decimal import Decimal

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement.line'

    amount_consumed = fields.Boolean(string='Importo Consumato', default=False)

    def action_consume_payment(self):
        for statement in self:
            for line in statement.line_ids:  # line -> account.move.line
                
                # Inizializza un dizionario vuoto per il debug
                debug = {}
                partnerTest = []
                
                importo = statement.amount #+ statement.amount_residual     
                debug['importo'] = importo

                partner = line.partner_id
                debug['partner'] = partner

                if not partner:
                    raise UserError("Nessun partner associato a questa riga dell'estratto conto.")
                
                # Trova le righe della fattura non pagate
                unpaid_lines = self.env['account.move.line'].search([
                    ('account_id', '=', partner.conto_id.id),
                    ('move_id.payment_state', '!=', 'paid')
                ])

                               
                # Calcola la somma dei valori del campo 'debit' per le righe delle fatture non pagate
                somma_quote = self.somma_quote_da_pagare(partner.conto_id.id)
                
                # Aggiungi i valori di debug al dizionario
                debug['somma_quote'] = somma_quote

                # Importante
                debug['linea_debito'] = [unpaid_line.debit for unpaid_line in unpaid_lines]

                k = 0
                for unpaid_line in unpaid_lines:

                    if importo >= unpaid_line.debit:
                        unpaid_line.move_id.payment_state = 'paid'
                        importo -= unpaid_line.debit
                        debug['payment_state'+k] = [unpaid_line.move_id.payment_state]
                        debug['riduzioni'+k] = [importo]
                    else:
                        if importo > 0:
                            unpaid_line.move_id.payment_state = 'partial'
                            debug['payment_state'] = unpaid_line.move_id.payment_state
                            importo = 0
                        else:
                            unpaid_line.move_id.payment_state = 'not_paid'
                            debug['payment_state'] = unpaid_line.move_id.payment_state
                    k += 1

                """
                for unpaid_line in unpaid_lines:
                    if importo >= unpaid_line.debit:                         
                        unpaid_line.move_id.payment_state = 'paid'
                        importo -= unpaid_line.debit
                        debug['primo_addebito'] = unpaid_line.debit
                        debug['importo_ridotto'] = importo
                    else:
                        if importo > 0:
                            statement.amount_residual = importo
                            debug['importo_residuo'] = importo
                            importo = 0
                        else:
                            statement.amount_residual = 0
                            debug['importo_consumato'] = importo
                        #unpaid_line.move_id.payment_state = 'partial'
                        break
                           
            statement.amount_consumed = True
            """

            raise UserError(str(debug))
        

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

    """
    def somma_quote_da_pagare(self, account_id):
        result = self.env['account.move.line'].read_group(
            domain=[
                ('account_id', '=', account_id),
                ('move_id.payment_state', '!=', 'paid')
            ],
            fields=['debit:sum'],
            groupby=[]
        )        
        return result[0]['debit'] 
    """
    def somma_quote_da_pagare(self, account_id):
        move_lines = self.env['account.move.line'].search([
            ('account_id', '=', account_id),
            ('move_id.payment_state', '!=', 'paid')
        ])
        somma_quote = sum(line.debit for line in move_lines)
        return somma_quote