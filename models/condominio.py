from odoo import models, fields, api

class AccountCondominium(models.Model):
    _inherit = 'res.partner'

 
    related_condominiums = fields.One2many(
        comodel_name='res.partner',
        inverse_name='condominium_id',
        string='Related Condominiums',
    )