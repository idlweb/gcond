from odoo import models, fields, api

class AccountCondominiumTable(models.Model):
    _name = 'account.condominio.table'

    account_condominio_id = fields.Many2one(
        'res.partner',
        string='Condominio',
        ondelete='cascade',
    )
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    condominio_id = fields.Many2one('account.condominio', string='Condominium')
    code_table = fields.Char(string='Code Table', required=True)
    unit_of_measure = fields.Char(string='Unit Of Measure')
    value_distribution = fields.Float(string='Value Distribution')