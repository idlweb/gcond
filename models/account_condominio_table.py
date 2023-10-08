from odoo import models, fields, api

class AccountCondominiumTable(models.Model):
    _name = 'account.condominio.table'

    unit_of_measure = fields.Char(string='Unit Of Measure')
    value_distribution = fields.Float(string='Value Distribution')
    quote = fields.Float(string='percentuale di competenza')
    table_id = fields.Many2one('account.condominio.table.master', string='Appartiene alla tabella',  required=False,)
    condominio_id = fields.Many2one('account.condomino',string='', required=False,)

   