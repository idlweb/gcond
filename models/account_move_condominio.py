"""
    With this Module we can use all the features of the account.move 
    and get the parameters to pass them to 'distribute_charges'
"""

from odoo import models, fields, api
from . import account_condominio_table_master

class AccountMove(models.Model):
    _inherit = 'account.move'

    distribution_table_id = fields.Many2one('account.condominio.table', string='Distribution Table')
    """
        sembra corretto anche il ricorso al 'code_table'
        ottengo la tabella intera ma il code_table da dove lo vado a prendere?
    """

    def distribute_charges(self, amount, table, document_number, account_id):
        charges = []

        # Check if the distribution table is set
        if not self.distribution_table_id:
            raise ValueError('The distribution table is not set for this invoice.')

        # Iterate over each condomino in the distribution table
        for line in self.distribution_table_id:
            condomino = line.condomino_id
            share = line.quote / 100.0
            charge = amount * share

            # Create a journal entry for the charge
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

        amount = self.amount_total
        table = self.distribution_table_id
        document_number = self.name
        account_id = self.env['account.account'].search([('code', '=', '410100')], limit=1).id

        self.distribute_charges(amount, table, document_number, account_id)