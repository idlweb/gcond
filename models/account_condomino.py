from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)
import pdb

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
    
    
    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company'), ('condomino','Condomino')],
        compute='_compute_company_type', inverse='_write_company_type')
    

   account_id = fields.Many2one(
        'account.account', string='conto_condomino',
        help="Utilizzo per contabilità")


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
        condominio = self.env['account.condominio'].browse(vals['condominio_id'])
        partner = super(GcondAccountCondomino, self).create(vals)
        if partner.is_condominio:
            account = self.env['account.account'].create({
                'name': f"{partner.name}-{condominio.name}-{partner.condominio_id.id}"
                'code': self.env['ir.sequence'].next_by_code('account.account'),
                'user_type_id': self.env.ref('account.data_account_type_receivable').id,
                'reconcile': True,
                'company_id': partner.company_id.id,
                'condominio_id': partner.condominio_id.id
            })
            partner.account_id = account.id
        return partner

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



      
