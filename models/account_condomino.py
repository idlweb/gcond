from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)
import pdb

class GcondAccountCondomino(models.Model):
    _name = 'account.condomino'
    _inherit = 'res.partner'
    
    
    condominio_id = fields.Many2one(
        comodel_name='account.condominio',
        string='Condomino',
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

    """
    def action_open_condominio_form(self):
        view_id = self.env.ref('gcond.view_condomino_form').id

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.condomino',
            'views': [(view_id, 'form')],
            'res_id': self.id,
            'target': 'current',
        }
    
    def post_init(self):
        for condomino in self:
            if condomino.action_open_condominio_executed:
                self.env['log'].info("=============>    La funzione action_open_condominio è stata eseguita per il condomino con ID", condomino.id)
    """


    @api.model
    def create(self, vals):
        # Imposta il valore del campo `commercial_partner_id` su un valore valido.
        if not vals.get('commercial_partner_id'):
            vals['commercial_partner_id'] = self.env['res.partner'].create({'name': 'Condominio'})
        #Crea un nuovo condominio.
        _logger.debug('===============================> Create a %s with vals %s', self._name, vals)
        record = super(GcondAccountCondomino, self).create(vals)  
            
        return record


    def action_register_condomino_form(self):
        view_id = self.env.ref('view_condomino_form').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.condomino',
            'views': [(view_id, 'form')],
            'res_id': self.id,
            'target': 'current',
        }

      
