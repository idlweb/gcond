from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)
import pdb
from odoo.exceptions import ValidationError, UserError

class GcondAccountCondomino(models.Model):
    #_name = 'account.condomino'
    _inherit = 'res.partner'


    is_condominio = fields.Boolean(string='is a Condominio', default=True,
        help="Check if the contact is a condominio, otherwise it is a person or a company")


    condominio_id = fields.Many2one(
        comodel_name='account.condominio',
        string='Condominio di appartenenza',
        ondelete='set null',
    )
    
    
    type_condomino = fields.Selection(
        [('affuttuario', 'Affittuario'), ('proprietario', 'Proprietario')],
        string='Tipologia condomino',
        default='proprietario',)
    
    conto_id = fields.Many2one(comodel_name='account.account', string='Contabilità', ondelete='set null')


    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company'), ('condomino','Condomino')],
        compute='_compute_company_type', inverse='_write_company_type')
    
    

    @api.depends('is_company')
    def _compute_company_type(self):
        for partner in self:
            if self.condominio_id:
                self.company_type = 'condomino'
                self.is_condominio = True
            else:
                partner.company_type = 'company' if partner.is_company else 'person'
                self.is_company = True
                self.is_condominio = False

    def _write_company_type(self):
        for partner in self:
            if partner.company_type == 'condomino':
               partner.is_condominio = True
            elif partner.company_type == 'company':
               partner.is_company = True
               

    @api.onchange('company_type')
    def onchange_company_type(self):
        if self.company_type == 'condomino':
           self.is_condominio = True
        else:
           self.is_company = (self.company_type == 'company')
    
    @api.onchange('condominio_id')
    def _onchange_condominio_id(self):
        if self.condominio_id and self.condominio_id.partner_id:
            self.parent_id = self.condominio_id.partner_id.id
            self.company_type = 'condomino'
            self.is_condominio = True
    

    @api.model_create_multi
    def create(self, vals_list):
        _logger.debug("Creating new partners with vals_list: %s", vals_list)
        for vals in vals_list:
            if vals.get('company_type') == 'condomino' or vals.get('condominio_id'):
                vals['is_condominio'] = True
                # Se è presente condominio_id, impostiamo il parent_id
                if vals.get('condominio_id'):
                    condominio = self.env['account.condominio'].browse(vals.get('condominio_id'))
                    if condominio.partner_id:
                        vals['parent_id'] = condominio.partner_id.id
        
        partners = super(GcondAccountCondomino, self).create(vals_list)
        
        for partner in partners:
            if partner.is_condominio and partner.condominio_id:
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
        # Se viene cambiato il condominio, aggiorniamo il parent_id
        if 'condominio_id' in vals:
            if vals.get('condominio_id'):
                condominio = self.env['account.condominio'].browse(vals.get('condominio_id'))
                if condominio.partner_id:
                    vals['parent_id'] = condominio.partner_id.id
            else:
                vals['parent_id'] = False
        
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
       

"""
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(GcondAccountCondomino, self).fields_view_get(view_id='view_condomino_form', view_type=view_type, toolbar=toolbar, submenu=submenu)

        if view_type == 'form' and res['model'] == 'res.partner':
            res['fields'].append({
                'name': 'is_condominio',
                'invisible': True,
                'on_change': 1,
                'modifiers': {'invisible': True},
                'id': 'is_condominio',
            })

        return res
"""



      
