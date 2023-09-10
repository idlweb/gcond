from odoo import models, fields, api
#from gcond import GcondAccountCondominium                  
from account_condominio import GcondAccountCondominium

class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_distribute_charges(self):
        """
        Distributes charges to condominiums based on the distribution table.

        Args:
            self: The current record.

        Returns:
            A dictionary of condominiums and their assigned charges.
        """

        amount = self.amount
        table = self.env['account.condominio.table'].search([('code_table', '=', self.code_table)], limit=1)
        document_number = self.document_number
        account_id = self.account_id

        charges = GcondAccountCondominium.distribute_charges(amount, table, document_number, account_id)        

        
        return charges