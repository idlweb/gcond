"""
    With this Module we can use all the features of the account.move 
    and get the parameters to pass them to 'distribute_charges'
"""

from odoo import models, fields, api
from . import account_condominio_table_master
from odoo.exceptions import ValidationError, UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    distribution_table_id = fields.Many2one('account.condominio.table', string='Distribution Table')
    """
        sembra corretto anche il ricorso al 'code_table'
        ottengo la tabella intera ma il code_table da dove lo vado a prendere?
    """

    
           
     