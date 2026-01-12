"""
    With this Module we can use all the features of the account.move 
    and get the parameters to pass them to 'distribute_charges'
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import format_amount
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    """
    def get_condominio_distribution_table(self, condominio_id):
        return self.distribution_table_ids.filtered(lambda table: table.condominio_id.id == condominio_id)
    """

    def distribute_charges(self, document_number):
        charges = []
        journal = self.journal_id
        if not journal or not journal.condominio_id:
            raise UserError("Il giornale deve essere associato a un condominio.")
        
        condominio_id = journal.condominio_id.id

        # Ciclo su ogni riga di costo (dare) della fattura
        for line in self.get_debit_entries():
            expense_type = line.account_id.expense_type_id
            if not expense_type:
                _logger.info("Nessun tipo di spesa associato al conto %s, salto la riga.", line.account_id.code)
                continue
            
            # Recuperiamo la tabella di ripartizione associata a questo tipo di spesa per questo condominio
            table_master = self.env['account.condominio.table.master'].search([
                ('condominio_id', '=', condominio_id),
                ('expense_type_id', '=', expense_type.id),
            ], limit=1)

            if not table_master:
                _logger.warning("Nessuna tabella di ripartizione trovata per il tipo spesa %s nel condominio %s", expense_type.name, journal.condominio_id.name)
                continue

            # Calcolo dell'importo base per questa tabella (applicando la percentuale del master)
            base_amount = (line.debit * table_master.percentuale) / 100.0
            # Divisione per 1000 millesimi
            millesimal_base = base_amount / 1000.0

            for row in table_master.table_ids:
                if not row.condomino_id:
                    continue
                
                # Quota = (Importo/1000) * Millesimi * % di competenza * 1.22 (IVA)
                charge = (millesimal_base * row.value_distribution * (row.quote / 100.0)) * 1.22
                
                if charge <= 0:
                    continue

                # Creazione della registrazione contabile di ripartizione (Avviso di Pagamento)
                # Harmonization: Usiamo la stessa data di scadenza della fattura originale
                due_date = self.invoice_date_due or fields.Date.today()
                
                account_move = self.env['account.move'].create({                        
                    'journal_id': self.journal_id.id,
                    'date': fields.Date.today(),
                    'ref' : f"AVVISO: {row.condomino_id.name}-{line.account_id.name}-{document_number}",
                    'move_type': 'entry',
                    'line_ids': [
                        (0, 0, {
                            'account_id': row.condomino_id.conto_id.id or row.condomino_id.property_account_receivable_id.id or line.account_id.id,
                            'partner_id': row.condomino_id.id,
                            'name': f"Ripartizione {document_number}",
                            'debit': charge,
                            'credit': 0.0,
                            'date_maturity': due_date, # Harmonizzazione scadenza
                        }),
                        (0, 0, {
                            'account_id': line.account_id.id,
                            'partner_id': row.condomino_id.id,
                            'name': f"Ripartizione {document_number}",
                            'credit': charge,
                            'debit': 0.0,
                        })
                    ],
                })
                charges.append(account_move)
                # Auto-post entry for immediate payment availability
                account_move.action_post()

        return charges

    # Non c'è bisogno di ricavere l'id del condominio dal nome del giornale perchè è già presente nel modello account.journal
    def get_condominio_id(self, journal_name):
        journal = self.env['account.journal'].search([('name', '=', journal_name)], limit=1)
        if not journal:
            raise ValueError('Journal not found.')
        return journal.condominio_id.id

    def button_distribute_charges(self):
        if self.state != 'posted':
            raise UserError('The invoice must be posted before distributing charges.')     
        document_number = self.name
        self.distribute_charges(document_number)

    def action_register_payment(self):
        # Ensure the move is posted before attempting payment
        if self.state == 'draft':
            self.action_post()
            
        # Target the receivable line (Credit side from resident perspective, Debit side in accounting logic for asset)
        # We must filter out lines that are already reconciled or have 0 residual to avoid "Nothing to pay" error
        receivable_lines = self.line_ids.filtered(lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled and l.amount_residual != 0)
        
        if not receivable_lines:
            # Fallback: try to find the line associated with the partner if account type is ambiguous
            # prioritizing lines with debit > 0 (debt) and not reconciled
            receivable_lines = self.line_ids.filtered(lambda l: l.partner_id and l.debit > 0 and not l.reconciled and l.amount_residual != 0)
            
        if not receivable_lines:
             # If we are here, it means everything is likely paid or the lines are weird.
             # Let's check if there are ANY lines for the partner to give a better error.
             paid_lines = self.line_ids.filtered(lambda l: l.partner_id and l.debit > 0 and l.reconciled)
             if paid_lines:
                 raise UserError("Questo avviso risulta già pagato!")
             raise UserError("Nessuna riga di credito da saldare trovata per questo avviso.")
             
        return receivable_lines.action_register_payment()
        
    def get_debit_entries(self):
        """
        Ottiene tutte le voci presenti nella sezione 'dare' (debit) della registrazione contabile.
        """
        debit_entries = self.line_ids.filtered(lambda line: line.debit > 0)
        return debit_entries

    def action_print_payment_receipt(self):
        """ Opens the linked payment receipt directly from the notice """
        self.ensure_one()
        
        # 1. Manual Traversal: Find payments linked via reconciliation
        payments = self.env['account.payment']
        
        # We look at all lines in the invoice (not just receivable, to be safe)
        for line in self.line_ids:
             # Check both debit and credit matches (Odoo stores partials in matched_debit_ids on the credit line)
             partials = line.matched_debit_ids + line.matched_credit_ids
             
             for partial in partials:
                  # Identify the counterpart line (the one that is NOT our line)
                  counterpart = partial.debit_move_id if partial.credit_move_id == line else partial.credit_move_id
                  
                  # Check if counterpart belongs to a payment
                  # Direct payment link
                  if counterpart.payment_id:
                       payments |= counterpart.payment_id
                  # Move-based payment link (Move -> Payment)
                  elif counterpart.move_id.payment_id:
                       payments |= counterpart.move_id.payment_id
        
        # 2. Fallback: helper method (if available)
        if not payments and hasattr(self, '_get_reconciled_payments'):
             payments = self._get_reconciled_payments()
             
        if not payments:
             raise UserError("Nessun pagamento collegato trovato (anche se l'avviso risulta pagato). Verifica la contabilità.")
        
        # Take the most recent payment
        # Sort by date desc
        last_payment = payments.sorted(key=lambda p: p.date, reverse=True)[0]
        
        # Custom Report for Notice Receipt
        return self.env.ref('gcond.action_report_payment_notice_receipt').report_action(self)

    def get_related_payments(self):
        """ Returns the payments related to this move (Notice) """
        self.ensure_one()
        payments = self.env['account.payment']
        
        # 1. Standard Odoo way (if reconciled)
        # Note: _get_reconciled_payments is a private method in some versions or might return partials.
        if hasattr(self, '_get_reconciled_payments'):
             payments |= self._get_reconciled_payments()
        
        # 2. Manual traversal (Robust way for our case)
        for line in self.line_ids.filtered(lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable')):
             partials = line.matched_debit_ids | line.matched_credit_ids
             for partial in partials:
                  counterpart = partial.debit_move_id if partial.credit_move_id == line else partial.credit_move_id
                  if counterpart.payment_id:
                       payments |= counterpart.payment_id
                  elif counterpart.move_id.payment_id:
                       payments |= counterpart.move_id.payment_id
        
        return payments

    def action_fix_payment_state(self):
        """ Forces recompute of payment state and prints debug info """
        for move in self:
            # 1. Force Invalidate
            move.invalidate_recordset(['payment_state', 'amount_residual'])
            move.line_ids.invalidate_recordset(['amount_residual', 'amount_residual_currency', 'reconciled'])
            
            # 2. Check conditions
            if move.amount_residual == 0 and move.payment_state != 'paid':
                # FORCE UPDATE via SQL
                # Sometimes Odoo computed fields get stuck. Using SQL bypasses the deadlock.
                self.env.cr.execute("UPDATE account_move SET payment_state='paid' WHERE id=%s", (move.id,))
                move.invalidate_recordset(['payment_state'])
                
        return {'type': 'ir.actions.client', 'tag': 'reload'}

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    """
    def action_register_payment(self):
        res = super(AccountPaymentRegister, self).action_create_payment()
        self._update_payment_state_and_reconcile()
        return res
    """
    def action_create_payments(self):
        # 1. Call super to create payments and get the action
        # Ensure latest code version is running
        action_vals = super(AccountPaymentRegister, self).action_create_payments()
        
        # 2. Extract created payment IDs from the action result
        payment_ids = []
        if isinstance(action_vals, dict):
            if action_vals.get('res_id'):
                payment_ids = [action_vals['res_id']]
            elif action_vals.get('domain'):
                for leaf in action_vals['domain']:
                    if isinstance(leaf, (list, tuple)) and len(leaf) == 3 and leaf[0] == 'id' and leaf[1] == 'in':
                        payment_ids = leaf[2]
                        break
        
        if not payment_ids:
            return action_vals

        payments = self.env['account.payment'].browse(payment_ids)

        # 3. Force reconciliation logic on the identified payments
        # self.line_ids contains the lines we selected to pay
        for payment in payments:
            # The payment creates a move (payment.move_id)
            # We need to find the credit line in the payment move that corresponds to the partner
            payment_move = payment.move_id
            payment_lines = payment_move.line_ids.filtered(lambda l: l.account_id.account_type in ('asset_receivable', 'liability_payable'))
            
            # We compare with the source lines being paid
            source_lines = self.line_ids
            
            for source_line in source_lines:
                # Find matching payment line (counterpart)
                # Ideally, accounts should match. If not, we fix the payment line.
                payment_line = payment_lines.filtered(lambda l: l.partner_id == source_line.partner_id)
                
                if payment_line:
                    # Fix Account Mismatch Refined:
                    # If payment used generic account but source was specific, we CANNOT change a posted move.
                    # We must unpost, change, repost.
                    if payment_line.account_id != source_line.account_id:
                         # Set to Draft to allow edit
                         payment_move.button_draft()
                         # Edit
                         payment_line.account_id = source_line.account_id
                         # Re-Post
                         payment_move.action_post()
                         
                         # Refresh payment_line after post
                         payment_line = payment_move.line_ids.filtered(lambda l: l.id == payment_line.id)
                    
                    # Force Reconciliation ONLY if not already reconciled
                    if not payment_line.reconciled and not source_line.reconciled:
                        (payment_line + source_line).reconcile()

        # 4. Force Update of Payment State on Source Moves
        # The forced reconciliation might not trigger the immediate recompute of payment_state 
        # on the invoice because of the complex draft/post cycle. We force it here.
        all_source_moves = self.line_ids.move_id
        if all_source_moves:
             all_source_moves.invalidate_recordset(['payment_state', 'amount_residual'])
             # Apply SQL Fix Logic Automatically
             for move in all_source_moves:
                  if move.amount_residual == 0 and move.payment_state != 'paid':
                      self.env.cr.execute("UPDATE account_move SET payment_state='paid' WHERE id=%s", (move.id,))
                      move.invalidate_recordset(['payment_state'])

        return action_vals


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    distribution_table_id = fields.Many2one(
        'account.condominio.table.master',
        string='Tabella Ripartizione',
        help='Tabella usata per ripartire questo costo.'
    )

    @api.onchange('account_id')
    def _onchange_account_id_gcond(self):
        for line in self:
            if not line.account_id or not line.account_id.expense_type_id:
                continue
            
            # Tentiamo di recuperare il condominio dal move (fattura)
            condominio_id = False
            if line.move_id and line.move_id.journal_id and line.move_id.journal_id.condominio_id:
                condominio_id = line.move_id.journal_id.condominio_id.id
            
            # Se siamo in un contesto dove il move non è ancora salvato, potremmo non avere il journal
            # Ma di solito in una fattura il journal è settato.
            
            if condominio_id:
                table = self.env['account.condominio.table.master'].search([
                    ('condominio_id', '=', condominio_id),
                    ('expense_type_id', '=', line.account_id.expense_type_id.id)
                ], limit=1)
                
                if table:
                    line.distribution_table_id = table.id
```
