from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)
import pdb

class GcondAccountCondomino(models.Model):
    _inherit = 'res.partner'

    is_condominio = fields.Boolean(string='is a Condominio', default=True,
        help="Check if the contact is a condominio, otherwise it is a person or a company")

    condominio_id = fields.Many2one(
        comodel_name='account.condominio',
        string='Condominio di appartenenza',
        ondelete='set null',
    )
    
    type_condomino = fields.Selection(
        [('affittuario', 'Affittuario'), ('proprietario', 'Proprietario')],
        string='Tipologia condomino',
        default='proprietario',
    )
    
    conto_id = fields.Many2one(comodel_name='account.account', string='Contabilità', ondelete='set null')

    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company'), ('condomino','Condomino')],
        compute='_compute_company_type', inverse='_write_company_type')

    @api.depends('is_company')
    def _compute_company_type(self):
        for partner in self:
            if partner.condominio_id:
                partner.company_type = 'condomino'
                partner.is_condominio = True
            else:
                partner.company_type = 'company' if partner.is_company else 'person'
                partner.is_company = True
                partner.is_condominio = False

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