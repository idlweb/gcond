"""
    Nella valutazione/analisi della natura dell'entita'
    condomino (proprietario/affittuario) non si evidenziano
    caratteristiche che lo rendano diverso dal partner, che ne è una astrazione
    pertanto sembra corretto estendere la classe.
    In odoo le tecniche di ererditarietà sono tre:
        a) aggiungo al'esistente e non ottengo una copia
        b) eredito e nomino e pertanto creo una classe/tabella (prototipo) nuova   =>  NO 
        c) Delegation: copio le difinizioni ma non la struttura                    =>  NO
        d) posso mettere in relazione 1:1 il condomino con un partner              =>  NO
"""

import logging 
_logger = logging.getLogger(__name__)
import pdb

from odoo import models, fields, api

class AccountCondominium(models.Model):
    _inherit = 'res.partner'




    condomino_id = fields.Many2one(
        comodel_name='account.condomino',
        string='Condominio',
    )


    type_condomino = fields.Selection(
        [('affuttuario', 'Affittuario'), ('proprietario', 'Proprietario')],
        string='Tipologia condomino',
        default='proprietario',)

        
    """
    # fix many2many da 'estensione ereditaria'
    tax_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='account_condominio_tax_rel',
        column1='condominio_id',
        column2='tax_id',
        string='Taxes', 
    )
    """
   

    