from odoo import models, fields, api
from odoo.exceptions import UserError
from decimal import Decimal

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement.line'

    amount_consumed = fields.Boolean(string='Importo Consumato', default=False)

    def action_consume_payment(self):
        for statement in self:
            i = 0
            for line in statement.line_ids:  # line -> account.move.line
                
                # Inizializza un dizionario vuoto per il debug
                debug = {}
                partnerTest = []
                
                partner = line.partner_id
                #debug['partner'] = partner

                if not partner:
                    raise UserError("Nessun partner associato a questa riga dell'estratto conto.")

                residual_sum = sum(lineR.amount_residual for lineR in statement.line_ids if lineR.partner_id == partner)
                importo = statement.amount #+ residual_sum
                #debug['importo'] = importo

                # Azzera i residui degli estratti conto precedenti
                previous_statements = self.env['account.bank.statement.line'].search([
                    ('partner_id', '=', partner.id),
                    ('amount_consumed', '=', True)
                ])
                for prev_statement in previous_statements:
                    prev_statement.amount_residual = 0
                
                
                
                # Trova le righe della fattura non pagate
                unpaid_lines = self.env['account.move.line'].search([
                    ('account_id', '=', partner.conto_id.id),
                    ('move_id.payment_state', '!=', 'paid'),
                    ('debit', '!=', 0),
                ], order='debit asc')

                               
                # Calcola la somma dei valori del campo 'debit' per le righe delle fatture non pagate
                #=> somma_quote = self.somma_quote_da_pagare(partner.conto_id.id)
                
                # Aggiungi i valori di debug al dizionario
                #=> debug['somma_quote'+str(i)] = somma_quote

                # Importante
                #=> debug['linea_debito'] = [unpaid_line.debit for unpaid_line in unpaid_lines]

                k = 0
                for unpaid_line in unpaid_lines:
                    if importo >= unpaid_line.debit:
                        k += 1
                        importo -= round(unpaid_line.debit, 2)
                        debug['ciclo:'+str(k)] = unpaid_line.move_id.id   
                        """
                            Appunti per il debug
                        """
                        #debug['importo_quota'+str(k)] = unpaid_line.debit         
                        #debug['stato'+str(k)] = unpaid_line.move_id.payment_state                        
                        #debug['verifica_residuo'+str(k)] = round(importo, 2) 
                        #debug['debito'+str(k)] = round(unpaid_line.debit, 2)
                    else:
                        if importo > 0:
                            line.amount_residual =  round(importo, 2)
                   

            for key, value in debug.items():
                self.mark_as_paid(value)

            statement.amount_consumed = True

            #raise UserError(str(debug))
        

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


    def mark_as_paid(self, move_id):
        move = self.env['account.move'].browse(move_id)
        move.payment_state = 'paid'
        self.env.cr.flush() 


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

    """ SOLUZIONE DIVERSA
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