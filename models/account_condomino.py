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
    

    
    # fix many2many da 'estensione ereditaria'
    channel_ids = fields.Many2many(
        relation='account_condomino_mail_partner_rel',
    )
  