from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)
import pdb

class GcondAccountCondomino(models.Model):
    _name = 'account.condomino'
    _inherit = 'res.partner'


    name = fields.Char(default='Nome contatto')

    condominio_id = fields.Many2one(
        comodel_name='account.condominio',
        string='Condominio di appartenenza',
        ondelete='set null',
    )

    
    type_condomino = fields.Selection(
        [('affuttuario', 'Affittuario'), ('proprietario', 'Proprietario')],
        string='Tipologia condomino',
        default='proprietario',)
    
    
    # fix many2many da 'estensione ereditaria'
    channel_ids = fields.Many2many(
        relation='account_condomino_mail_partner_rel',
    )

    
    commercial_partner_id = fields.Many2one(
        'account.condominio', string='Commercial Entity',
        compute='_compute_commercial_partner',
        recursive=True, index=True)

    """
    @api.depends('is_company', 'parent_id.commercial_partner_id')
    def _compute_commercial_partner(self):
        for partner in self:
            if partner.is_company or not partner.parent_id:
                partner.commercial_partner_id = partner
    """

    """
    @api.depends('is_company', 'parent_id.commercial_partner_id')
    def _compute_commercial_partner(self):
        for partner in self:
            if partner.is_company or not partner.parent_id:
                partner.commercial_partner_id = self.env['res.partner'].create({
                    'name': partner.name,
                    'is_company': partner.is_company,
                    'parent_id': partner.parent_id,
                })
    """

    _sql_constraints = []

    @api.depends('is_company', 'parent_id.commercial_partner_id')
    def _compute_commercial_partner(self):
        for partner in self:
            if partner.is_company or not partner.parent_id:
                condomino = self.env['account.condomino'].create({
                    'name': partner.name,
                    'is_company': partner.is_company,
                    'parent_id': partner.parent_id,
                })

                partner.commercial_partner_id = self.env['account.condomino'].browse(18) #condomino.id
            else:
                partner.commercial_partner_id = partner.parent_id.commercial_partner_id

    """
    @api.depends('is_company', 'parent_id.commercial_partner_id')
    def _compute_commercial_partner(self):
        for partner in self:
            if partner.is_company or not partner.parent_id:
                partner.commercial_partner_id = partner.env['res.partner'].search([('name', '=', partner.name)], limit=1)
    """
  

     
    @api.model
    def create(self, vals):
        record = super(GcondAccountCondomino, self).create(vals)  
        # Imposta il valore del campo `commercial_partner_id` su un valore valido.
      
        #Crea un nuovo condominio.                    
        return record
    


      
