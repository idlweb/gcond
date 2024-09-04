"""
    With this Module we can use all the features of the account.move 
    and get the parameters to pass them to 'distribute_charges'
"""

from odoo import models, fields, api
#.  from . import account_condominio_table_master
from odoo.exceptions import ValidationError, UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    #distribution_table_ids = fields.One2many('account.condominio.table', string='Distribution Table')


    """
    def get_condominio_distribution_table(self, condominio_id):
        return self.distribution_table_ids.filtered(lambda table: table.condominio_id.id == condominio_id)
    """
    

    def distribute_charges(self, document_number):
        charges = []
        context = self.env.context
        #raise UserError(context)
        
        journal = self.journal_id
        condominio_id = journal.condominio_id.id
        
        # Iterate over each cost line. get_debit_entries() contiene tutte le voci presenti nella sezione 'dare' (debit) della registrazione contabile. 
        for line in self.get_debit_entries():
  
            # Get the amount of the cost entry
            amount = line.debit
            #raise UserError(line.account_id)
            # Get the account_condominio_table_master record associated with the debit/cost entry
            account_condominio_table = self.env['account.condominio.table.master'].search([
                ('condominio_id', '=', condominio_id),
                #('account_ids', 'in', [line.account_id.id])
            ])
            raise UserError(condominio_id)
            if not account_condominio_table:
                raise UserError("No account_condominio_table_master record found for current condominium and cost entry.")

            
            for dettaglio_ripartizione in account_condominio_table:
                raise UserError("Accesso al blocco dei records")
                amount = (amount * account_condominio_table.percentuale)/100

                """
                unit_of_measure = fields.Char(string='Unit Of Measure')
                value_distribution = fields.Float(string='Value Distribution')
                quote = fields.Float(string='Percentuale di Competenza')
                table_id = fields.Many2one('account.condominio.table.master', string='Appartiene alla Tabella', required=False)
                condomino_id = fields.Many2one('res.partner', string='Condomino', required=False)
                """

                account_condominio_table_records = self.env['account.condominio.table'].search([
                    ('table_id', '=', dettaglio_ripartizione.id),
                ])

                amount = amount / 1000 

                for account_condominio_table_record in account_condominio_table_records:
                    # Calculate the share for the partner
                    
                    charge = (amount * account_condominio_table_record.value_distribution)*quote/100
                    
                    raise UserError(charge)

                    # Create a journal entry for the charge
                    account_move = self.env['account.move'].create({
                        'journal_id': self.journal_id,
                        'date': fields.Date.today(),
                        'line_ids': [
                            {
                                'account_id': line.account_id.id,
                                'partner_id': account_condominio_table_record.condomino_id.id,
                                'name': document_number,
                                'debit': charge,
                            }
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

    """
    def check_account_entries(self, debit_entries):
        account_ids = self.distribution_table_id.account_ids
        debit_entries = debit_entries.filtered(lambda account: account.account_id in account_ids.mapped('account_id'))
        return debit_entries
    """    
     