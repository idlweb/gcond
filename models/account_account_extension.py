from odoo import models, fields

class AccountAccount(models.Model):
    _inherit = 'account.account'

    expense_type_id = fields.Many2one(
        'gcond.expense.type',
        string='Tipo di Spesa Condominiale',
        help='Associa questo conto a una tipologia di spesa (es. Acqua, Luce) per l\'automazione delle tabelle millesimali.'
    )
