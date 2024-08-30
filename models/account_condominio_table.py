from odoo import models, fields, api

class AccountCondominiumTable(models.Model):
    _name = 'account.condominio.table'

    unit_of_measure = fields.Char(string='Unit Of Measure')
    value_distribution = fields.Float(string='Value Distribution')
    quote = fields.Float(string='Percentuale di Competenza')
    table_id = fields.Many2one('account.condominio.table.master', string='Appartiene alla Tabella', required=False)
    condomino_id = fields.Many2one('res.partner', string='Condomino', required=False)

   
 
    