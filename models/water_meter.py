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
    move_id = fields.Many2one('account.move', string='Registrazione Contabile')

    @api.depends('reading_general_end', 'reading_general_start')
    def _compute_general_consumption(self):
        for rec in self:
            rec.consumption_general = max(0, rec.reading_general_end - rec.reading_general_start)

    def action_fetch_meters(self):
        """Populate lines with all divisional meters and their latest readings as Start Reading."""
        self.ensure_one()
        self.line_ids.unlink()
        
        meters = self.env['gcond.water.meter'].search([
            ('condominio_id', '=', self.condominio_id.id),
            ('meter_type', '=', 'divisional')
        ])
        
        lines = []
        for meter in meters:
            # Find reading for Start Date (closest <= date_start)
            start_reading = self.env['gcond.water.reading'].search([
                ('meter_id', '=', meter.id),
                ('date', '<=', self.date_start)
            ], order='date desc', limit=1)
            
            # Find reading for End Date (closest <= date_end)
            end_reading = self.env['gcond.water.reading'].search([
                ('meter_id', '=', meter.id),
                ('date', '<=', self.date_end)
            ], order='date desc', limit=1)

            # Fallback to initial_reading if no history found for Start
            val_start = start_reading.value if start_reading else meter.initial_reading
            
            # For End, use found reading, or default to Start (0 consumption) if nothing new found
            val_end = end_reading.value if end_reading else val_start

            lines.append((0, 0, {
                'meter_id': meter.id,
                'partner_id': meter.partner_id.id,
                'reading_start': val_start,
                'reading_end': val_end,
            }))
        
        self.line_ids = lines

    def action_calculate(self):
        """Perform Normalization and Pricing"""
        self.ensure_one()
        if self.consumption_general <= 0:
            raise UserError(_("Il consumo generale deve essere maggiore di zero."))

        total_measured = sum(line.consumption_measured for line in self.line_ids)
        
        if total_measured <= 0:
             raise UserError(_("Nessun consumo rilevato dai sottocontatori."))

        # Coefficient (K) = General / Sum(Divisional)
        k_normalization = self.consumption_general / total_measured
        
        for line in self.line_ids:
            # 1. Normalize
            line.consumption_normalized = line.consumption_measured * k_normalization
            
            # 2. Apply Pricing (Scaglioni)
            cost = 0.0
            remaining_consumption = line.consumption_normalized
            
            # Sort tariffs just in case
            sorted_tariffs = self.tariff_ids.sorted('limit_from')
            
            for tier in sorted_tariffs:
                if remaining_consumption <= 0:
                    break
                
                # Calculate m3 in this tier
                # Tier size = limit_to - limit_from
                tier_size = tier.limit_to - tier.limit_from
                
                consumable = min(remaining_consumption, tier_size)
                cost += consumable * tier.price
                remaining_consumption -= consumable
                
            line.amount = cost

        self.state = 'calculated'

    expense_account_id = fields.Many2one('account.account', string='Conto di Contropartita (Costo)', required=False, 
                                         help="Conto da accreditare (es. Spese Acqua o Fornitore)")

    def action_post(self):
        """Generate Accounting Entries"""
        self.ensure_one()
        if not self.journal_id:
             raise UserError(_("Seleziona un diario per la registrazione."))
        if not self.expense_account_id:
             # Try to find a default 'Water' account or raise error
             pass 
             # For now, let's require it or let the user set it.

        move_lines = []
        # 1. Total Credit to Expense Account (Reversal of Cost)
        total_amount = sum(line.amount for line in self.line_ids)
        
        move_lines.append((0, 0, {
            'account_id': self.expense_account_id.id,
            'name': f"Ripartizione Acqua: {self.name}",
            'credit': total_amount,
            'debit': 0.0,
        }))

        # 2. Debit to Residents
        for line in self.line_ids:
            if line.amount <= 0.01:
                continue
                
            move_lines.append((0, 0, {
                'account_id': line.partner_id.property_account_receivable_id.id,
                'partner_id': line.partner_id.id,
                'name': f"Acqua: {line.meter_id.name} ({line.reading_start} -> {line.reading_end})",
                'debit': line.amount,
                'credit': 0.0,
            }))

        # Create the Move
        move = self.env['account.move'].create({
            'journal_id': self.journal_id.id,
            'date': fields.Date.today(),
            'ref': self.name,
            'move_type': 'entry',
            'line_ids': move_lines,
        })
        
        move.action_post()
        self.move_id = move.id
        self.state = 'posted'
        move.action_post()
        self.move_id = move.id
        self.state = 'posted'
        return True

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
