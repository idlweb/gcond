from odoo import models, fields, api

class GcondAccountCondominium(models.Model):
    _name = 'gcond.account.condominium'
    _inherit = 'account.account'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')

    property_account_register_id = fields.Many2one(
        'account.account.register',
        string='Registro di registrazione',
        required=True,
    )

   document_number = fields.Char(string='Document Number')
account_id = fields.Many2one('account.account', string='Account')

@api.multi
def distribute_charges(self, amount, table, document_number, account_id):
    """
    Distributes charges to condominiums based on the distribution table.

    Args:
        amount: The total amount of the charge.
        table: The distribution table.
        document_number: The document number.
        account_id: The account ID.

    Returns:
        A dictionary of condominiums and their assigned charges.
    """

    charges = {}
    for condominium in self.related_condominiums:
        # Get the condominium's share of the charge.
        share = table.get(condominium.code_table)
        if share is None:
            # The condominium is not included in the distribution table.
            continue

        # Calculate the condominium's charge.
        charge = amount * share

        # Create a journal entry for the charge.
        account_move = self.env['account.move'].create({
            'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
            'date': fields.Date.today(),
            'line_ids': [
                {
                    'account_id': condominium.account_id.id,
                    'name': condominium.name,
                    'debit': charge,
                },
                {
                    'account_id': account_id,
                    'name': 'Spese condominiali',
                    'credit': charge,
                },
            ],
        })

        # Add the charge to the dictionary of charges.
        charges[condominium] = charge

    return charges
