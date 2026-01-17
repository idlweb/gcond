from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from datetime import datetime

class GcondF24ExportWizard(models.TransientModel):
    _name = 'gcond.f24.export.wizard'
    _description = 'Wizard Export F24'

    condominio_id = fields.Many2one('account.condominio', string='Condominio', required=True)
    journal_id = fields.Many2one('account.journal', string='Banca', domain="[('type', '=', 'bank')]", required=True)
    date_payment = fields.Date(string='Data Scadenza', default=fields.Date.today, required=True)
    
    # Selection of moves
    withholding_move_ids = fields.Many2many('withholding.tax.move', string='Ritenute da Versare', 
                                            domain="[('state', '=', 'due')]")

    # Result
    file_data = fields.Binary(string='File F24', readonly=True)
    file_name = fields.Char(string='File Name', readonly=True)

    @api.onchange('condominio_id', 'date_payment')
    def _onchange_filter_moves(self):
        """ Auto-select moves based on logic (previous month competence usually) """
        if not self.condominio_id:
            return
            
        # Simplified Logic: Fetch ALL 'due' moves for this condominio/company
        # We need to filter by Company associated with Condominio?
        # Assuming Condominio has a Company or we use the Journal's company.
        
        # Filtering logic:
        # Usually we pay the previous month's competence.
        # But let's just show ALL due for now.
        
        domain = [
            ('state', '=', 'due'),
            # We need to link Condominio to WT Move. 
            # WT Move has 'company_id'. Condominio is not on WT move directly unless we added it?
            # WT Move -> Payment Line -> Move -> Journal -> Condominio?
            # Let's try to trace it.
        ]
        
        # Logic to trace Condominio:
        # withholding.tax.move -> payment_line_id (account.move.line) -> move_id (account.move) -> journal_id (account.journal) -> condominio_id
        
        # This is expensive for search. Better to search python side for small datasets?
        # Or search moves first.
        
        pass

    def action_generate_file(self):
        self.ensure_one()
        if not self.withholding_move_ids:
            raise UserError(_("Seleziona almeno una ritenuta da versare."))

        # 1. Group by Tax Code (e.g. 1040) AND Month/Year Competence
        # The user example: 51 01 1019 00 01 2025 ...
        # Means we group by Code + Month + Year.
        
        grouped_data = {} # Key: (Code, Month, Year) -> Value: Total Amount
        
        for move in self.withholding_move_ids:
            # Code
            wt_code = move.withholding_tax_id.code
            # Competence Date (Reference Period)
            # Use 'date' field of wt move
            comp_date = move.date
            if not comp_date:
                comp_date = fields.Date.today() # Fallback
            
            month = comp_date.strftime('%m')
            year = comp_date.strftime('%Y')
            
            key = (wt_code, month, year)
            
            if key not in grouped_data:
                grouped_data[key] = 0.0
            grouped_data[key] += move.amount

        # 2. Generate Content
        lines = []
        
        # Header (Record 10)? User didn't request, but usually needed.
        # Let's generate purely the Record 51 lines as requested by the example for first iteration.
        # "Tracciato CBI" is complex. If user provided "Esempio Record 51", they might want just that fragment
        # OR the full file. I'll include headers placeholders if I can, but user example was SPECIFIC on 51.
        # I'll output just the 51 lines for now to match verify.
        
        # Mapping:
        # 51 (2)
        # 01 (2) - Let's fix this as '01' (Sezione Erario Rigo 1)
        # Code (4)
        # 00 (2)
        # Month (2)
        # Year (4)
        # Amount (16) - Zero padded, 2 decimals implied
        # Zeros (12)
        
        row_count = 0
        for (code, month, year), amount in grouped_data.items():
            row_count += 1
            # Clean code (remove spaces, ensure 4 chars)
            code_str = code.strip().replace(' ', '')
            if len(code_str) > 4:
                code_str = code_str[:4] # Truncate or warn? 1040 is 4.
            code_str = code_str.ljust(4, '0') # Or rjust? usually codes like 1040 are numeric.
            
            # Formattazione Importo: 123.45 -> 12345
            amount_cents = int(round(amount * 100))
            amount_str = str(amount_cents).zfill(16)
            
            # Line Construction
            # 51
            # 01
            # CODE (4)
            # 00
            # MM (2)
            # YYYY (4)
            # AMOUNT (16)
            # ZEROS (12)
            
            # Total Length: 2+2+4+2+2+4+16+12 = 44 chars.
            
            line = f"5101{code_str}00{month}{year}{amount_str}{'0'*12}"
            lines.append(line)
        
        content = "\r\n".join(lines)
        
        # 3. Save
        self.file_data = base64.b64encode(content.encode('utf-8'))
        self.file_name = f"F24_{self.condominio_id.name}_{self.date_payment}.txt"
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'gcond.f24.export.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_mark_paid(self):
        """ Marks selected moves as Paid """
        for move in self.withholding_move_ids:
            move.action_paid()
        return {'type': 'ir.actions.client', 'tag': 'reload'}
