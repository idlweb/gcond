"""
    With this Module we can use all thr features of the account.move 
    and get the parameters to pass theme at 'distribuite_charges'
"""


from odoo import models, fields, api

from . import account_condominio_table_master

class AccountMove(models.Model):
    _inherit = 'account.move'

    """
        sembra corretto anche il ricorso al 'code_table'
        ottengo la tabella intera ma il code_table da dove lo vado a prendere?
    """

    def distribute_charges(self, amount, table, document_number, account_id):
        charges = []

        # Check if the condominium is included in the distribution table.
        if table.get(self.id) is None:
            raise ValueError('The condominium is not included in the distribution table.')

        # Calculate the condominium's share of the charge.
        share = table.get(self.id)
        charge = amount * share

        # Create a journal entry for the charge.
        account_move = self.env['account.move'].create({
            'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
            'date': fields.Date.today(),
            'line_ids': [
                {
                    'account_id': self.account_id.id,
                    'name': self.name,
                    'debit': charge,
                },
                {
                    'account_id': account_id,
                    'name': 'Spese condominiali',
                    'credit': charge,
                },
            ],
        })

        # Add the charge to the list of charges.
        charges.append(account_move)

        return charges


    def button_distribute_charges(self):
        #Aggiunta la verifica sullo stato bozza 
        if self.state != 'draft':
            raise ValueError('The invoice must be in draft state.')
        
        move = self
        amount = move.get('amount')
        # TO-DO da dove prendo self.code_table 
        # Ip.n1 -> lo prendiamo dal context (vediamo quando
        # inserirlo)
        """
            move.id -> journal_id -> condominio_id

        """
        table = self.env['account.condominio.table.master'].search([('account_id', '=', self.id)], limit=1)
        document_number = self.document_number
        account_id = self.account_id
        charges = self.distribute_charges(amount, table, document_number, account_id)        


        """
            Una nuova forma di dialogo con l'utente...
        """
        if charges:
            message = 'The expenses have been successfully distributed to the condominiums.'
        else:
            message = 'There are no condominiums to distribute the expenses to.'

        #return charges

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Expenses Distribution',
                'message': message,
                'type': 'info',
            },
        }

        
   

    

        