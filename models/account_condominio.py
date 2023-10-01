"""
    questa tabella rappresenta il condominio
    TO-DO: erediterà da res.partner e non da account.
    In odoo account.account rappresenta il piano dei conti
"""
from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)
import pdb

class GcondAccountCondominium(models.Model):
    _name = 'account.condominio'
    #_inherit = 'account.account'

    
    name = fields.Char(string='Name', required=True) # se eredito da partner non serve
    code = fields.Char(string='Code', required=True) # ok
    description = fields.Text(string='Description')  # se eredito da partner non serve
    address = fields.Char(string='Indirizzo')        # se eredito da partner non serve
    email = fields.Char(string='Email', help='Indirizzo email del condominio', required=False) # se eredito da partner non serve
    vat = fields.Char(string='VAT', required=True)   # se eredito da partner non serve
    city = fields.Char(string='City', required=True) # se eredito da partner non serve
    zip = fields.Char(string='ZIP', required=True)   # se eredito da partner non serve
    phone = fields.Char(string='Phone')              # se eredito da partner non serve
    
    
    type_registration = fields.Selection(
        [('fattura', 'Fattura'), ('ricevuta', 'Ricevuta')],
        string='Tipo Registrazione',
        default='fattura',)
    
    
    
    journal_id = fields.Many2one(
        'account.journal',
        string='Giornale',
        required=False,
    )
    
    # pdb.set_trace()

    """
    account_condominio_id = fields.Many2one(
        'account.account',
        string='Account Condominio',
        ondelete='cascade',
    )
    """

    """
    # fix many2many da 'estensione ereditaria'
    tax_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='account_condominio_tax_rel',
        column1='account_id',
        column2='tax_id',
        string='Taxes',
    )
    """

    """
    condominio_id = fields.Many2one(
        'res.partner',
        string='Condominio',
        ondelete='cascade',
    )
    """
    
   
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country',
        required=False)
   



    
    receivable_account_id = fields.Many2one(
        'account.account', string='Conto credito', required=False,
        help='Conto di credito del condominio')
    

    
    payable_account_id = fields.Many2one(
        'account.account', string='Conto debito', required=True,
        help='Conto di debito del condominio')
    

    #document_number = fields.Char(string='Document Number')
    #account_id = fields.Many2one('account.account', string='Account')

    @api.model
    def action_register_condominium(self):
        #Azione per registrare un condominio.
        view_id = self.env.ref('view_account_condominium_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registra condominio',
            'res_model': 'account.condominio',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
        }
   
    """
    @api.model
    def action_accounting(self):
        #Azione per gestire la contabilità dei condomini.
        #_logger.debug('verifica id utilizzatoin action_accounting %d', self.env.ref('view_account_condominium_accounting').id)
        view_id = self.env.ref('view_account_condominium_accounting').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contabilità condominio',
            'res_model': 'account.condominio',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
        }
    """

    
    @api.model
    def create(self, vals):
        #Crea un nuovo condominio.
        record = super(GcondAccountCondominium, self).create(vals)

        # Imposta il conto di credito del condominio.
        record.receivable_account_id = self.env['account.account'].search([
            ('code', '=', '250100'),
        ], limit=1)

        # Imposta il conto di debito del condominio.
        record.payable_account_id = self.env['account.account'].search([
            ('code', '=', '250100'),
        ], limit=1)
    
        #Crea un nuovo condominio.
        record = super(GcondAccountCondominium, self).create(vals)

        # Imposta la tipologia di registrazione di default.
        """ capire il senso di questa istruzione"""
        #record.type_registration = 'debit'

        return record
    

    
    #@api.multi
    def distribute_charges(self, amount, table, document_number, account_id):
        charges = {}
        for condominium in self.related_condominiums:
            # Get the condominium's share of the charge.
            share = table.get(condominium.code_table)
            if share is None:
                # The condominium is not included in the distribution table.
                continue

            # Calculate the condominium's charge.
            charge = amount * share

            # Create a journal entry for the charge.
            account_move = self.env['account.move'].create({
                'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
                'date': fields.Date.today(),
                'line_ids': [
                    {
                        'account_id': condominium.account_id.id,
                        'name': condominium.name,
                        'debit': charge,
                    },
                    {
                        'account_id': account_id,
                        'name': 'Spese condominiali',
                        'credit': charge,
                    },
                ],
            })

            # Add the charge to the dictionary of charges.
            charges[condominium] = charge

        return charges
        