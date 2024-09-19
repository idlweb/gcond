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
    

    @api.model
    def create(self, vals):
        _logger.debug("Creating a new partner with vals: %s", vals)
        condominio = self.env['account.condominio'].browse(vals['condominio_id'])
        partner = super(GcondAccountCondomino, self).create(vals)
        partner.is_condominio = True
        company_id = self.env.user.company_id.id
        if partner.is_condominio:
            sequence_code = 'account.account.condomino'
            account_code = self.env['ir.sequence'].next_by_code(sequence_code)
            if not account_code:
                _logger.error("Sequence with code '%s' not found", sequence_code)
                raise ValueError(f"Sequence with code '{sequence_code}' not found")
            ass_account = self.env['account.account'].create({
                'name': f"{partner.name}-{condominio.name}",
                'code': account_code,
                'user_type_id': self.env.ref('account.data_account_type_receivable').id,
                'reconcile': True,
                'company_id':company_id,
                #'condominio_id': partner.condominio_id.id,
            })
            partner.conto_id = ass_account.id
            
        return partner

    @api.model
    def action_view_account_situation(self, *args):
        name = self.get_account_by_partner_name(self.name)
        # Trova il conto associato al partner
        account = self.env['account.account'].search([('name', 'ilike', name)], limit=1)
        if not account:
            raise UserError("Nessun conto trovato per questo partner.")
        
        # Restituisci l'azione per aprire la vista del conto
        return {
            'type': 'ir.actions.act_window',
            'name': 'Situazione Contabile',
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
            'domain': [('account_id', '=', account.id)],
            'context': dict(self.env.context),
        }
       
    def get_account_by_partner_name(self, partner_name):
        account = self.env['account.account'].search([('name', 'ilike', partner_name)], limit=1)
        if not account:
            raise UserError(f"Nessun conto trovato per il partner con nome '{partner_name}'.")
        return account

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



      
