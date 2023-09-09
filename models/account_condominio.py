from odoo import models, fields, api

class GcondAccountCondominium(models.Model):
    _name = 'gcond.account.condominium'
    _inherit = 'account.account'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    
    property_account_register_id = fields.Many2one(
        'account.account.register',
        string='Registro di registrazione',
        required=True,
    )
