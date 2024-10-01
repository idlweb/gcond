from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement.line'

    amount_consumed = fields.Boolean(string='Importo Consumato', default=False)

    def action_consume_payment(self):
        for statement in self:
            for line in statement.line_ids:  # line -> account.move.line
                                
                debug = []

                importo = statement.amount               
                partner = line.partner_id                    
                if not partner:
                    raise UserError("Nessun partner associato a questa riga dell'estratto conto.")

                # Trova le righe della fattura non pagate
                unpaid_lines = self.env['account.move.line'].search([
                    ('account_id', '=', partner.conto_id.id),
                    ('move_id.payment_state', '!=', 'paid')
                ])
            
                # Calcola la somma dei valori del campo 'debit' per le righe delle fatture non pagate
                somma_quote = self.somma_quote_da_pagare(partner.conto_id.id)
                #
                #if not unpaid_lines:
                #    raise UserError("Non ci sono quote non pagate per questo partner.")

                
                debug.append(somma_quote) # ok
                debug.append("^")
                debug.append(importo)     # ok
                
                """
                    logica di calcolo:
                    -non ci sono valori residui da pagare ma valori residui da consumare
                    -considerare se il valore da pagare è minore del valore residuo
                    primo debito -> unpaid_line.debit o unpaid_line.balance
                """

                for unpaid_line in unpaid_lines:
                    debug.append(unpaid_line.debit)
                    debug.append("^")  
                    if statement.amount  >= unpaid_line.debit:
                        importo = importo - unpaid_line.debit 
                        unpaid_line.move_id.write({'payment_state': 'paid'})
                        debug.append("^") 
                        debug.append(unpaid_line.move_id.payment_state)
                        debug.append("____") 
                        debug.append(importo)  # ok              
                    else:                        
                        if importo >= 0:
                            statement.amount_residual = importo
                            debug.append("^") 
                            debug.append(statement.amount_residual) 
                        break
                    
                raise UserError(debug)

                # Aggiorna lo stato della riga dell'estratto conto
                statement.amount_consumed = True

                # Crea una scrittura contabile
                """
                move_vals = {
                    'journal_id': statement.journal_id.id,
                    'date': fields.Date.context_today(self),
                    'line_ids': [
                        (0, 0, {
                            'account_id': partner.property_account_receivable_id.id,
                            'partner_id': partner.id,
                            'credit': line.amount,
                            'debit': 0,
                        }),
                        (0, 0, {
                            'account_id': self.env['account.account'].search([('name', 'ilike', partner.name)], limit=1).id,
                            'partner_id': partner.id,
                            'credit': 0,
                            'debit': line.amount,
                        }),
                    ],
                }
                self.env['account.move'].create(move_vals)
                """
  
    def somma_quote_da_pagare(self, id):
        # Calcola la somma dei valori del campo 'debit' per le righe delle fatture non pagate
        debit_sum = self.env['account.move.line'].read_group(
            domain=[
                ('account_id', '=',id),
                ('move_id.payment_state', '!=', 'paid')
            ],
            fields=['debit:sum'],
            groupby=[]
        )[0]['debit']
        return debit_sum
    