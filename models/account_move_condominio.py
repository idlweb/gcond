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
            account_condominio_tables = self.env['account.condominio.table.master'].search([
                ('condominio_id', '=', condominio_id),
            ])
                       

            for account_condominio_table in account_condominio_tables:
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

    """
    def action_register_payment(self):
        res = super(AccountPaymentRegister, self).action_create_payment()
        self._update_payment_state_and_reconcile()
        return res
    """
    def _create_payments(self):
          # Recupera il contesto
        context = self.env.context
        # Recupera gli ID dei record selezionati
        active_ids = context.get('active_ids', [])
        # Recupera i record di fattura selezionati
        invoices = self.env['account.move'].browse(active_ids)
        # Esegui operazioni sui record di fattura selezionati
        for invoice in invoices:
            res = super(AccountPaymentRegister, self)._create_payments()
            self._update_payment_state_and_reconcile(invoice.name)

        """
        Creates payments based on the provided values and updates the payment state.

        This method overrides the `_create_payments` method from the `AccountPaymentRegister` class.
        It first calls the superclass method to create the payments and then updates the payment state
        and reconciles using the provided communication reference.

        Accessible fields from the instance (`self`):
        - self.payment_date: The date of the payment.
        - self.amount: The amount of the payment.
        - self.payment_type: The type of the payment.
        - self.partner_type: The type of the partner.
        - self.communication: The communication reference for the payment.
        - self.journal_id: The journal associated with the payment.
        - self.currency_id: The currency used for the payment.
        - self.partner_id: The partner associated with the payment.
        - self.partner_bank_id: The bank account of the partner.
        - self.payment_method_line_id: The payment method line used for the payment.
        - self.line_ids: The lines associated with the payment, where the first line's account ID is used as the destination account ID.

        Returns:
            The result of the superclass `_create_payments` method.
      
        """
       
        return res

    def _update_payment_state_and_reconcile(self, key_update_move):
        # Find the account.move line using the name field
        move_lines = self.env['account.move'].search([('name', '=', key_update_move)])
        for move_line in move_lines:
            # Update the payment state to 'paid'
            move_line.payment_state = 'paid'
            # Reconcile the entries
            # self._reconcile_entries(move_line)

    def _reconcile_entries(self, move):
        lines_to_reconcile = move.line_ids.filtered(lambda l: l.account_id.reconcile)
        if lines_to_reconcile:
            lines_to_reconcile.reconcile()
