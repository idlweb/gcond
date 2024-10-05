from odoo import models, fields, api
from odoo.exceptions import UserError
from decimal import Decimal

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement.line'

    amount_consumed = fields.Boolean(string='Importo Consumato', default=False)

    def action_consume_payment(self):
        for statement in self:
            for line in statement.line_ids:  # line -> account.move.line
                
                # Inizializza una lista vuota per il debug
                debug = []
                partnerTest = []
                
                importo = statement.amount #+ statement.amount_residual               
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
                
                raise UserError(somma_quote)
                # Aggiungi i valori di debug alla lista
                debug.append("-somma_quote:"+str(somma_quote))
                #debug.append("-importo estratto:"+str(importo))

                
                """
                    logica di calcolo:
                    -non ci sono valori residui da pagare ma valori residui da consumare
                    -considerare se il valore da pagare è minore del valore residuo
                    primo debito -> unpaid_line.debit o unpaid_line.balance
                """             
                
                for unpaid_line in unpaid_lines:
                    if importo >= unpaid_line.debit:
                        debug.append("-primo addebito:"+str(unpaid_line.debit))
                        importo -= unpaid_line.debit 
                        unpaid_line.move_id.payment_state = 'paid'
                        debug.append("-importo ridotto:"+str(importo))
                    else:
                        if importo > 0:
                            statement.amount_residual = importo
                            debug.append("-residuo importo>0:"+str(importo))
                            importo = 0
                        else:
                            statement.amount_residual = 0
                            debug.append("-residuo:"+str(importo))
                        #unpaid_line.move_id.payment_state = 'partial'
                        break

            statement.amount_consumed = True
            raise UserError(debug)
        

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
        return result[0]['debit'] 