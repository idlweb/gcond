from odoo import models, fields, api

class AccountCondominium(models.Model):
    _inherit = 'res.partner'

    """
    condominium_id = fields.Many2one(
        comodel_name='account.condominio',
        string='Condominium',
    )
 
    related_condominiums = fields.One2many(
        comodel_name='res.partner',
        inverse_name='condominium_id',
        string='Related Condominiums',
    )
    """