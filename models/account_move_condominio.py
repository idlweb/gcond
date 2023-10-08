"""
    With this Module we can use all thr features of the account.move 
    and get the parameters to pass theme at 'distribuite_charges'
"""


from odoo import models, fields, api

from . import account_condominio

class AccountMove(models.Model):
    _inherit = 'account.move'

    """
        sembra corretto anche il ricorso al 'code_table'
        ottengo la tabella intera
    """
    def button_distribute_charges(self):
        amount = self.amount
        table = self.env['account.condominio.table'].search([('code_table', '=', self.code_table)], limit=1)
        document_number = self.document_number
        account_id = self.account_id

        instAC = account_condominio.GcondAccountCondominium()
        charges = instAC.distribute_charges(amount, table, document_number, account_id)        

        return charges
   