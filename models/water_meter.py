from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class GcondWaterMeter(models.Model):
    _name = 'gcond.water.meter'
    _description = 'Contatore Acqua'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Matricola (Numero Serie)', required=True)
    description = fields.Char(string='Descrizione / Ubicazione')
    condominio_id = fields.Many2one('account.condominio', string='Condominio', required=True)
    
    installation_date = fields.Date(string='Data Installazione/Sostituzione')
    initial_reading = fields.Float(string='Lettura Iniziale (alla posa)', default=0.0)
    
    # Type: General (Main) or Divisional (Sub-meter)
    meter_type = fields.Selection([
        ('general', 'Generale (Acquedotto)'),
        ('divisional', 'Divisionale (Residente)')
    ], string='Tipo Contatore', default='divisional', required=True)

    # For divisional meters
    partner_id = fields.Many2one('res.partner', string='Residente Assegnato', 
                                 domain="[('condominio_id', '=', condominio_id)]")

    @api.onchange('condominio_id')
    def _onchange_condominio_id(self):
        """Reset partner when condo changes to avoid inconsistencies"""
        if self.condominio_id:
            self.partner_id = False
            # Optional: Return domain explicitly if needed, but field domain handles it.
            return {'domain': {'partner_id': [('condominio_id', '=', self.condominio_id.id)]}}
        else:
            return {'domain': {'partner_id': []}}
    


    reading_ids = fields.One2many('gcond.water.reading', 'meter_id', string='Letture')

    last_reading_date = fields.Date(string='Data Ultima Lettura', compute='_compute_last_reading', store=True)
    last_reading_value = fields.Float(string='Ultima Lettura (m3)', compute='_compute_last_reading', store=True)

    @api.depends('reading_ids.date', 'reading_ids.value')
    def _compute_last_reading(self):
        for meter in self:
            last_reading = self.env['gcond.water.reading'].search([
                ('meter_id', '=', meter.id)
            ], order='date desc, id desc', limit=1)
            meter.last_reading_date = last_reading.date
            meter.last_reading_value = last_reading.value

class GcondWaterReading(models.Model):
    _name = 'gcond.water.reading'
    _description = 'Lettura Contatore'
    _order = 'date desc, id desc'

    meter_id = fields.Many2one('gcond.water.meter', string='Contatore', required=True, ondelete='cascade')
    date = fields.Date(string='Data Lettura', required=True, default=fields.Date.context_today)
    value = fields.Float(string='Lettura (m3)', required=True)
    
    distribution_id = fields.Many2one('gcond.water.distribution', string='Ripartizione Collegata', ondelete='set null')

    _sql_constraints = [
        ('value_positive', 'CHECK(value >= 0)', 'La lettura non può essere negativa.')
    ]

class GcondWaterTariff(models.Model):
    _name = 'gcond.water.tariff'
    _description = 'Scaglione Tariffario Acqua'
    _order = 'limit_from asc'

    distribution_id = fields.Many2one('gcond.water.distribution', string='Ripartizione', ondelete='cascade')
    name = fields.Char(string='Descrizione Scaglione', required=True)
    limit_from = fields.Float(string='Da (m3)', required=True)
    limit_to = fields.Float(string='A (m3)', required=True, help="Usa 999999 per infinito")
    price = fields.Float(string='Prezzo unitario (€/m3)', required=True)

class GcondWaterDistribution(models.Model):
    _name = 'gcond.water.distribution'
    _description = 'Ripartizione Acqua'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Descrizione', required=True, default=lambda self: _('Ripartizione Acqua %s') % fields.Date.today())
    condominio_id = fields.Many2one('account.condominio', string='Condominio', required=True)
    date_start = fields.Date(string='Data Inizio Periodo', required=True)
    date_end = fields.Date(string='Data Fine Periodo', required=True)
    state = fields.Selection([
        ('draft', 'Da Calcolare'),
        ('calculated', 'Calcolato'),
        ('posted', 'Contabilizzato')
    ], string='Stato', default='draft', tracking=True)

    # General Meter Logic
    meter_general_id = fields.Many2one('gcond.water.meter', string='Contatore Generale', 
                                       domain="[('condominio_id', '=', condominio_id), ('meter_type', 'in', ('general', False))]")
    
    reading_general_start = fields.Float(string='Lettura Iniziale Generale', help="Lettura precedente dell'acquedotto")
    reading_general_end = fields.Float(string='Lettura Finale Generale', help="Lettura attuale dell'acquedotto")
    
    consumption_general = fields.Float(string='Consumo Fatturato (m3)', compute='_compute_general_consumption', store=True, readonly=False)
    
    # Additional Costs (Fisso, Fognatura, Depurazione) to be distributed purely by m3 or other logic
    # Simplified: User enters Total Bill amount if they want logic to match bill exactly?
    # User Request: "riparametrazione m3" then "scaglioni".
    
    line_ids = fields.One2many('gcond.water.distribution.line', 'distribution_id', string='Dettaglio Residenti')
    tariff_ids = fields.One2many('gcond.water.tariff', 'distribution_id', string='Scaglioni Tariffari')

    # Accounting
    journal_id = fields.Many2one('account.journal', string='Diario', domain="[('type', '=', 'general')]")
    move_id = fields.Many2one('account.move', string='Registrazione Contabile') # Deprecated? Keeping for compatibility or single entry fallback
    invoice_ids = fields.One2many('account.move', 'water_distribution_id', string='Avvisi di Pagamento Generati')

    def action_post(self):
        """Generate Customer Invoices (Avvisi di Pagamento) for Residents"""
        self.ensure_one()
        if not self.journal_id:
             raise UserError(_("Seleziona un diario per la registrazione."))
        
        # We need a Product to put on the invoice line? Not strictly, can use label + account.
        # Account to Credit (Income side) -> The Expense Account (to reverse cost)
        if not self.expense_account_id:
             raise UserError(_("Seleziona il conto di costo/spesa per il recupero."))

        invoices = []
        
        for line in self.line_ids:
            if line.amount <= 0.01:
                continue
            
            # Create Invoice for this Partner
            inv_vals = {
                'partner_id': line.partner_id.id,
                'move_type': 'out_invoice',
                'journal_id': self.journal_id.id,
                'date': fields.Date.today(),
                'invoice_date': fields.Date.today(),
                'ref': f"{self.name} - {line.meter_id.name}",
                'water_distribution_id': self.id,
                'invoice_line_ids': [(0, 0, {
                    'name': f"Ripartizione Acqua: {line.meter_id.name} ({line.reading_start} -> {line.reading_end})",
                    'quantity': 1,
                    'price_unit': line.amount,
                    'account_id': self.expense_account_id.id, # Credit this account
                })]
            }
            # Add Taxes? Usually internal distribution is tax-exempt or handled upstream. 
            # If Expense Account has taxes... beware. For now, assume no tax on distribution line.
            
            # Create
            invoice = self.env['account.move'].create(inv_vals)
            invoices.append(invoice)

        # Notify user or just set state
        self.state = 'posted'
        
        # Optional: Return action to view created invoices
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', [inv.id for inv in invoices])]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices[0].id
            
        return action

    def action_print(self):
        return self.env.ref('gcond.action_report_water_distribution').report_action(self)

class GcondWaterDistributionLine(models.Model):
    _name = 'gcond.water.distribution.line'
    _description = 'Riga Ripartizione Acqua'

    distribution_id = fields.Many2one('gcond.water.distribution', string='Ripartizione', required=True, ondelete='cascade')
    meter_id = fields.Many2one('gcond.water.meter', string='Contatore')
    partner_id = fields.Many2one('res.partner', string='Residente')
    
    reading_start = fields.Float(string='Lettura Precedente')
    reading_end = fields.Float(string='Lettura Attuale')
    
    consumption_measured = fields.Float(string='Consumo Rilevato (m3)', compute='_compute_consumption', store=True)
    consumption_normalized = fields.Float(string='Consumo Addebitato (m3)', help="Ricalcolato in base al contatore generale")
    
    amount = fields.Float(string='Importo (€)')

    @api.depends('reading_end', 'reading_start')
    def _compute_consumption(self):
        for line in self:
            line.consumption_measured = max(0, line.reading_end - line.reading_start)

class AccountMove(models.Model):
    _inherit = 'account.move'

    water_distribution_id = fields.Many2one('gcond.water.distribution', string='Ripartizione Acqua', ondelete='set null')
