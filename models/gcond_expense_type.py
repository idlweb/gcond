from odoo import models, fields

class GcondExpenseType(models.Model):
    _name = 'gcond.expense.type'
    _description = 'Tipo di Spesa Condominiale'

    name = fields.Char(string='Nome Tipo Spesa', required=True, translate=True)
    code = fields.Char(string='Codice', required=True)
    description = fields.Text(string='Descrizione')
    sequence = fields.Integer(string='Sequenza', default=10)
