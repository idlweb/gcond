from odoo import models, fields, api

class AccountCondominium(models.Model):
    _inherit = 'res.partner'

    account_condominio_id = fields.Many2one(
        'res.partner',
        string='Condominio',
        ondelete='cascade',
    )
    
    """
    condomino_id = fields.Many2one(
        comodel_name='account.condomino',
        string='Condomino',
    )
 
    related_condominiums = fields.One2many(
        comodel_name='res.partner',
        inverse_name='condomino_id',
        string='Related Condominiums',
    )
 
    # fix many2many da 'estensione ereditaria'
    tax_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='account_condominio_tax_rel',
        column1='condominio_id',
        column2='tax_id',
        string='Taxes', 
    )
    """

    