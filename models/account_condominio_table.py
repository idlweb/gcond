from odoo import models, fields, api

class AccountCondominiumTable(models.Model):
    _name = 'account.condominio.table'

    table_id = fields.Many2one(
        'account.condominio.table.master',
        string='testata',
        required=False,
        inverse='',
    )

    unit_of_measure = fields.Char(string='Unit Of Measure')
    value_distribution = fields.Float(string='Value Distribution')
    quote = fields.Float(string='percentuale di competenza')
    