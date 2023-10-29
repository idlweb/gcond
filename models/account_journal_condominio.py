"""
    questa tabella è il luogo in cui associo
    in journal ad un condominio
"""
from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)
import pdb

class AccountJournalCondominio(models.Model):
    _inherit = 'account.journal'
    #add
    condominio_id = fields.Many2one('account.condominio', string='Condominio')