"""
    With this Module we can use all the features of the account.move 
    and get the parameters to pass them to 'distribute_charges'
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    """
    def get_condominio_distribution_table(self, condominio_id):
        return self.distribution_table_ids.filtered(lambda table: table.condominio_id.id == condominio_id)
    """

    def distribute_charges(self, document_number):
        charges = []
        context = self.env.context
        #raise UserError(context)
        
        journal = self.journal_id
        if not journal:
            raise UserError("Journal not found.")
        
        condominio_id = journal.condominio_id.id

        # Da approfondire
        # debit_entries = debit_entries.filtered(lambda account: account.account_id in account_ids.mapped('account_id'))
        """"""
        # Iterate over each cost line. get_debit_entries() contiene tutte le voci presenti nella sezione 'dare' (debit) della registrazione contabile. 
        for line in self.get_debit_entries():
  
            # Get the amount of the cost entry
            amount = line.debit
            # raise UserError(line.account_id)
            # Get the account_condominio_table_master record associated with the debit/cost entry
            account_condominio_table = self.env['account.condominio.table.master'].search([
                ('condominio_id', '=', condominio_id),
            ])
           
            if not account_condominio_table:
                raise UserError("No account_condominio_table_master record found for current condominium and cost entry.")
                       
            for dettaglio_ripartizione in account_condominio_table:
                amount = (amount * account_condominio_table.percentuale)/100
                
                if line.account_id.id in dettaglio_ripartizione.account_ids.ids:
                    account_condominio_table_records = self.env['account.condominio.table'].search([
                        ('table_id', '=', dettaglio_ripartizione.id),
                    ])

                    amount = amount / 1000 

                    for account_condominio_table_record in account_condominio_table_records:
                        # Calculate the share for the partner
                        
                        charge = ((amount * (account_condominio_table_record.value_distribution * account_condominio_table_record.quote / 100))) * 1.22
                        
                        # Create a journal entry for the charge
                        account_move = self.env['account.move'].create({                        
                            'journal_id': self.journal_id.id, #PURCHASE[18]
                            'date': fields.Date.today(),
                            'ref' : f"{account_condominio_table_record.condomino_id.name}-{line.account_id.name}",
                            'move_type': 'entry',
                            'line_ids': [
                                (0, 0, {
                                    'account_id': account_condominio_table_record.condomino_id.conto_id.id,
                                    'partner_id': account_condominio_table_record.condomino_id.id,
                                    'name': document_number, # etichetta
                                    #'analytic_account_id': account_condominio_table_record.condomino_id.id,  # Assegna il conto analitico
                                    'debit': charge,
                                    'credit': 0.0,
                                }),
                                (0, 0, {
                                    'account_id': line.account_id.id,
                                    'partner_id': account_condominio_table_record.condomino_id.id,
                                    'name': document_number,
                                    #'analytic_account_id': account_condominio_table_record.condomino_id.id,  # Assegna il conto analitico
                                    'credit': charge,
                                    'debit': 0.0,
                                })
                            ],
                        })

                        charges.append(account_move)
                        
                                            
        return charges

    # Non c'è bisogno di ricavere l'id del condominio dal nome del giornale perchè è già presente nel modello account.journal
    def get_condominio_id(self, journal_name):
        journal = self.env['account.journal'].search([('name', '=', journal_name)], limit=1)
        if not journal:
            raise ValueError('Journal not found.')
        return journal.condominio_id.id

    def button_distribute_charges(self):
        if self.state != 'posted':
            raise UserError('The invoice must be posted before distributing charges.')     
        document_number = self.name
        self.distribute_charges(document_number)
        
    def get_debit_entries(self):
        """
        Ottiene tutte le voci presenti nella sezione 'dare' (debit) della registrazione contabile.
        """
        debit_entries = self.line_ids.filtered(lambda line: line.debit > 0)
        return debit_entries

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self):
        res = super(AccountPaymentRegister, self)._create_payments()
        self._update_payment_state_and_reconcile()
        return res

    def _update_payment_state_and_reconcile(self):
        for payment in self.env['account.payment'].search([]):
            for move in payment.move_id:
                for line in move.line_ids:
                    if line.account_id.code.startswith('150') and line.account_id.user_type_id.type in ('receivable', 'payable'):
                        line.move_id.payment_state = 'paid'
                        line.move_id.invoice_ids.filtered(lambda inv: inv.id == line.move_id.id).state = 'paid'
                #self._reconcile_entries(move, payment)

    def _reconcile_entries(self, move, payment):
        lines_to_reconcile = (move.line_ids + payment.move_line_ids).filtered(lambda l: l.account_id.reconcile)
        if lines_to_reconcile:
            lines_to_reconcile.reconcile()   
