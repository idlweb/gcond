"""
    With this Module we can use all the features of the account.move 
    and get the parameters to pass them to 'distribute_charges'
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
                    'name': self.name,
                    'credit': charge,
                },
            ],
        })

        charges.append(account_move)
        return charges

    def button_distribute_charges(self):
        if self.state != 'posted':
            raise UserError('The invoice must be posted before distributing charges.')

        # Example parameters, these should be dynamically determined
        amount = self.amount_total
        table = self.env['account.condominio.table'].get_distribution_table(self.id)
        document_number = self.name
        account_id = self.env['account.account'].search([('code', '=', '400000')], limit=1).id

        self.distribute_charges(amount, table, document_number, account_id)