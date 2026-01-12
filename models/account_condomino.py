from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError, UserError

class GcondAccountCondomino(models.Model):
    _inherit = 'res.partner'

    is_condominio = fields.Boolean(
        string='È un Edificio (Condominio)', 
        default=False,
        help="Seleziona se questo contatto rappresenta l'intero edificio")

    condominio_id = fields.Many2one(
        comodel_name='account.condominio',
        string='Appartiene al Condominio',
        ondelete='set null',
        help="Il condominio (edificio) a cui appartiene questo contatto"
    )
    
    type_condomino = fields.Selection(
        [('affuttuario', 'Affittuario'), ('proprietario', 'Proprietario')],
        string='Tipologia condomino',
        default='proprietario',)
    
    conto_id = fields.Many2one(
        comodel_name='account.account', 
        string='Contabilità', 
        ondelete='set null')

    @api.depends('name', 'parent_id.name', 'condominio_id')
    def _compute_display_name(self):
        super()._compute_display_name()
        for partner in self:
            if partner.condominio_id:
                partner.display_name = partner.name

    @api.onchange('condominio_id')
    def _onchange_condominio_id(self):
        if self.condominio_id:
            self.is_condominio = False
            if self.condominio_id.partner_id:
                self.parent_id = self.condominio_id.partner_id.id
        else:
            self.parent_id = False

    @api.onchange('is_condominio')
    def _onchange_is_condominio(self):
        if self.is_condominio:
            self.condominio_id = False
            self.is_company = True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('condominio_id'):
                vals['is_condominio'] = False
                condominio = self.env['account.condominio'].browse(vals.get('condominio_id'))
                if condominio.partner_id:
                    vals['parent_id'] = condominio.partner_id.id
            if vals.get('is_condominio'):
                vals['condominio_id'] = False
                vals['is_company'] = True
        
        partners = super(GcondAccountCondomino, self).create(vals_list)
        
        for partner in partners:
            if partner.condominio_id:
                sequence_code = 'account.account.condomino'
                account_code = self.env['ir.sequence'].next_by_code(sequence_code)
                if not account_code:
                    _logger.error("Sequence with code '%s' not found", sequence_code)
                    continue
                
                ass_account = self.env['account.account'].with_company(partner.company_id or self.env.company).create({
                    'name': f"{partner.name}-{partner.condominio_id.name}",
                    'code': account_code,
                    'account_type': 'asset_receivable',
                    'reconcile': True,
                })
                partner.conto_id = ass_account.id
                
        return partners

    def write(self, vals):
        if 'condominio_id' in vals:
            if vals.get('condominio_id'):
                condominio = self.env['account.condominio'].browse(vals.get('condominio_id'))
                if condominio.partner_id:
                    vals['parent_id'] = condominio.partner_id.id
                vals['is_condominio'] = False
            else:
                vals['parent_id'] = False
        
        if vals.get('is_condominio'):
            vals['condominio_id'] = False
            vals['is_company'] = True
            
        return super(GcondAccountCondomino, self).write(vals)

    def action_view_account_situation(self):
        self.ensure_one()
        if not self.conto_id:
            raise UserError("Nessun conto contabile associato a questo condomino.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Situazione Contabile: {self.name}',
            'res_model': 'account.move.line',
            'view_mode': 'list,form',
            'domain': [('account_id', '=', self.conto_id.id)],
            'context': dict(self.env.context, search_default_account_id=self.conto_id.id),
        }

    def action_open_full_view(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
