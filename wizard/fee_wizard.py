# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class GcondFeeWizardLine(models.TransientModel):
    _name = 'gcond.fee.wizard.line'
    _description = 'Riga Quota Condominiale'

    wizard_id = fields.Many2one('gcond.fee.wizard', string='Wizard Reference', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Condomino', required=True)
    amount = fields.Monetary(string='Importo Versato', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='wizard_id.journal_id.currency_id')

class GcondFeeWizard(models.TransientModel):
    _name = 'gcond.fee.wizard'
    _description = 'Registrazione Massiva Quote Condominiali'

    condominio_id = fields.Many2one('account.condominio', string='Condominio', required=True)
    journal_id = fields.Many2one('account.journal', string='Banca/Cassa', domain=[('type', 'in', ('bank', 'cash'))], required=True)
    payment_date = fields.Date(string='Data Pagamento', default=fields.Date.context_today, required=True)
    
    line_ids = fields.One2many('gcond.fee.wizard.line', 'wizard_id', string='Quote')

    @api.onchange('condominio_id')
    def _onchange_condominio_id(self):
        if not self.condominio_id:
            self.line_ids = False
            return
        
        # Pre-fill lines with all residents of the condominium
        lines = []
        # Find all partners linked to this condominio (via parent_id or distinct logic if refined)
        # Using the standard parent_id logic for residents
        residents = self.env['res.partner'].search([
            ('condominio_id', '=', self.condominio_id.id)
        ])
        
        for resident in residents:
            lines.append((0, 0, {
                'partner_id': resident.id,
                'amount': 0.0,
            }))
        
        self.line_ids = lines

    def action_confirm_payments(self):
        self.ensure_one()
        _logger.info("Conferma pagamenti massivi per condominio %s", self.condominio_id.name)
        payments_to_create = []
        
        for line in self.line_ids:
            if line.amount > 0:
                # Determine destination account (Dedicated Resident Account)
                dest_account_id = line.partner_id.conto_id.id or line.partner_id.property_account_receivable_id.id
                
                payment_vals = {
                    'date': self.payment_date,
                    'amount': line.amount,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'memo': f"Quota {self.payment_date} - {self.condominio_id.name}",
                    'journal_id': self.journal_id.id,
                    'currency_id': self.journal_id.currency_id.id or self.journal_id.company_id.currency_id.id,
                    'partner_id': line.partner_id.id,
                    'destination_account_id': dest_account_id, # EXPLICIT ASSIGNMENT
                }
                payments_to_create.append(payment_vals)
        
        if not payments_to_create:
            raise UserError(_("Nessuna quota inserita (importo > 0)."))

        # Create batch payments
        Payment = self.env['account.payment']
        payments = Payment.create(payments_to_create)
        payments.action_post()
        
            'type': 'ir.actions.act_window',
            'name': 'Riscossioni Create',
            'res_model': 'account.payment',
            'view_mode': 'list,form',
            'domain': [('id', 'in', payments.ids)],
        }
