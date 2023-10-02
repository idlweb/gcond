from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)
import pdb

class GcondAccountCondomino(models.Model):
    _name = 'account.condomino'
    _inherit = 'res.partner'
    
    
    condominio_id = fields.Many2one(
        comodel_name='account.condominio',
        string='Condomino',
        ondelete='set null',
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