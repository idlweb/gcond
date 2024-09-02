from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    distribution_table_id = fields.Many2one('account.condominio.table', string='Distribution Table')

    def distribute_charges(self, amount, table, document_number, account_id):
        charges = []

        # Check if the distribution table is set
        if not table:
            raise ValueError('The distribution table is not set for this invoice.')

        # Iterate over each condomino in the distribution table
        for line in table:
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
        document_number = self.name
        account_id = self.env['account.account'].search([('code', '=', '410100')], limit=1).id

        # Get the cost lines associated with the invoice
        cost_lines = self.line_ids.filtered(lambda line: line.account_id.code == 'COST_CODE')

        # Iterate over each cost line and distribute the charges
        for line in cost_lines:
            # Check if the cost line is associated with the distribution table
            table = line.distribution_table_id or self.distribution_table_id

            if not table:
                raise UserError('The distribution table is not set for this cost line or the invoice.')

            self.distribute_charges(line.debit, table, document_number, account_id)

        return True