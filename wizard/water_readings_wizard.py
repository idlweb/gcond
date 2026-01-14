from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WaterReadingsWizard(models.TransientModel):
    _name = 'gcond.water.readings.wizard'
    _description = 'Wizard Inserimento Letture Massive'

    condominio_id = fields.Many2one('account.condominio', string='Condominio', required=True)
    date = fields.Date(string='Data Lettura', required=True, default=fields.Date.context_today)
    line_ids = fields.One2many('gcond.water.readings.wizard.line', 'wizard_id', string='Letture')

    @api.onchange('condominio_id')
    def _onchange_condominio_id(self):
        if not self.condominio_id:
            self.line_ids = False
            return
        
        meters = self.env['gcond.water.meter'].search([
            ('condominio_id', '=', self.condominio_id.id),
            ('meter_type', '=', 'divisional')
        ])
        
        lines = []
        for meter in meters:
            last_reading = self.env['gcond.water.reading'].search([
                ('meter_id', '=', meter.id)
            ], order='date desc', limit=1)
            
            lines.append((0, 0, {
                'meter_id': meter.id,
                'partner_id': meter.partner_id.id,
                'previous_reading': last_reading.value if last_reading else 0.0,
                'previous_date': last_reading.date if last_reading else False,
                # Default current reading to previous to speed up minor checks? No, better allow 0 or empty.
                'current_reading': last_reading.value if last_reading else 0.0, 
            }))
        
        self.line_ids = lines

    def action_confirm(self):
        self.ensure_one()
        Reading = self.env['gcond.water.reading']
        count = 0
        
        for line in self.line_ids:
            # Skip if no change and reading is same as previous (assuming no update needed)
            # OR allow entering same reading (zero consumption)
            
            # Validation: Warn if new < old?
            if line.current_reading < line.previous_reading:
                # This could be a meter reset or error. For now, let's allow it but maybe log?
                # Or block? Usually block.
                # raise UserError(_("La lettura per %s è inferiore alla precedente!") % line.meter_id.name)
                pass 

            # Only create if there is a value (even 0 if it's a first reading)
            # Logic: If current_reading is DIFFERENT from previous, or force entry?
            # Let's create an entry for every line to confirm "we checked this meter on this date".
            
            Reading.create({
                'meter_id': line.meter_id.id,
                'date': self.date,
                'value': line.current_reading,
            })
            count += 1
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Letture Create'),
                'message': _('%s letture inserite correttamente.') % count,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

class WaterReadingsWizardLine(models.TransientModel):
    _name = 'gcond.water.readings.wizard.line'
    _description = 'Riga Wizard Letture'

    wizard_id = fields.Many2one('gcond.water.readings.wizard', string='Wizard', required=True, ondelete='cascade')
    meter_id = fields.Many2one('gcond.water.meter', string='Contatore', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Residente', readonly=True)
    
    previous_reading = fields.Float(string='Lettura Prec.', readonly=True)
    previous_date = fields.Date(string='Data Prec.', readonly=True)
    
    current_reading = fields.Float(string='Nuova Lettura', required=True)
