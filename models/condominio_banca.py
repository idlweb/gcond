from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    amount_consumed = fields.Boolean(string='Importo Consumato', default=False)

    @api.mmodel
    def action_consume_payment(self):
        for statement in self:
            for line in statement.line_ids:
                if self.env.context.get('active_id') == line.id:
                    partner = line.partner_id
                    if not partner:
                        raise UserError("Nessun partner associato a questa riga dell'estratto conto.")

                    # Trova le righe della fattura non pagate
                    unpaid_lines = self.env['account.move.line'].search([
                        ('partner_id', '=', partner.id),
                        ('payment_state', '!=', 'paid')
                    ])
                    if not unpaid_lines:
                        raise UserError("Non ci sono quote non pagate per questo partner.")

                    # Applica il pagamento alle quote
                    amount_to_consume = line.amount
                    for unpaid_line in unpaid_lines:
                        if amount_to_consume <= 0:
                            break
                        amount_to_pay = min(amount_to_consume, unpaid_line.amount_residual)
                        unpaid_line.amount_residual -= amount_to_pay
                        amount_to_consume -= amount_to_pay
                        if unpaid_line.amount_residual <= 0:
                            unpaid_line.payment_state = 'paid'

                    # Aggiorna lo stato della riga dell'estratto conto
                    line.amount_consumed = True

                    # Crea una scrittura contabile
                    """
                    move_vals = {
                        'journal_id': statement.journal_id.id,
                        'date': fields.Date.context_today(self),
                        'line_ids': [
                            (0, 0, {
                                'account_id': partner.property_account_receivable_id.id,
                                'partner_id': partner.id,
                                'credit': line.amount,
                                'debit': 0,
                            }),
                            (0, 0, {
                                'account_id': self.env['account.account'].search([('name', 'ilike', partner.name)], limit=1).id,
                                'partner_id': partner.id,
                                'credit': 0,
                                'debit': line.amount,
                            }),
                        ],
                    }
                    self.env['account.move'].create(move_vals)
                    """