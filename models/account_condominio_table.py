from odoo import models, fields, api

class AccountCondominiumTable(models.Model):
    _name = 'gcond.account.condominium.table'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    condominium_id = fields.Many2one('gcond.account.condominium', string='Condominium')
    code_table = fields.Char(string='Code Table', required=True)
    unit_of_measure = fields.Char(string='Unit Of Measure')
    value_distribution = fields.Float(string='Value Distribution')