"""
    With this Module we can use all the features of the account.move 
    and get the parameters to pass them to 'distribute_charges'
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
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

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    """
    def action_register_payment(self):
        res = super(AccountPaymentRegister, self).action_create_payment()
        self._update_payment_state_and_reconcile()
        return res
    """
    def _create_payments(self):
          # Recupera il contesto
        context = self.env.context
        # Recupera gli ID dei record selezionati
        active_ids = context.get('active_ids', [])
        # Recupera i record di fattura selezionati
        invoices = self.env['account.move'].browse(active_ids)
        # Esegui operazioni sui record di fattura selezionati
        for invoice in invoices:
            res = super(AccountPaymentRegister, self)._create_payments()
            self._update_payment_state_and_reconcile(invoice.name)

        """
        Creates payments based on the provided values and updates the payment state.

        This method overrides the `_create_payments` method from the `AccountPaymentRegister` class.
        It first calls the superclass method to create the payments and then updates the payment state
        and reconciles using the provided communication reference.

        Accessible fields from the instance (`self`):
        - self.payment_date: The date of the payment.
        - self.amount: The amount of the payment.
        - self.payment_type: The type of the payment.
        - self.partner_type: The type of the partner.
        - self.communication: The communication reference for the payment.
        - self.journal_id: The journal associated with the payment.
        - self.currency_id: The currency used for the payment.
        - self.partner_id: The partner associated with the payment.
        - self.partner_bank_id: The bank account of the partner.
        - self.payment_method_line_id: The payment method line used for the payment.
        - self.line_ids: The lines associated with the payment, where the first line's account ID is used as the destination account ID.

        Returns:
            The result of the superclass `_create_payments` method.
      
        """
       
        return res

    def _update_payment_state_and_reconcile(self, key_update_move):
        # Find the account.move line using the name field
        move_lines = self.env['account.move'].search([('name', '=', key_update_move)])
        for move_line in move_lines:
            # Update the payment state to 'paid'
            move_line.payment_state = 'paid'
            # Reconcile the entries
            # self._reconcile_entries(move_line)

    def _reconcile_entries(self, move):
        lines_to_reconcile = move.line_ids.filtered(lambda l: l.account_id.reconcile)
        if lines_to_reconcile:
            lines_to_reconcile.reconcile()


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
