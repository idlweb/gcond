from odoo import models, fields, api

class GcondAccountCondominium(models.Model):
    _name = 'account.condominio'
    #_inherit = 'account.account'

    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    address = fields.Char(string='Indirizzo')
    email = fields.Char(string='Email', help='Indirizzo email del condominio', required=False)
    vat = fields.Char(string='VAT', required=True)
    city = fields.Char(string='City', required=True)
    zip = fields.Char(string='ZIP', required=True)
    phone = fields.Char(string='Phone')
    
    """
    type_registration = fields.Selection(
        [('fattura', 'Fattura'), ('ricevuta', 'Ricevuta')],
        string='Tipo Registrazione',
        default='fattura',)
    """
    
    """
    journal_id = fields.Many2one(
        'account.journal',
        string='Giornale',
        required=False,
    )
    """

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
   
    
    """
    property_account_register_id = fields.Many2one(
        'account.account.register',
        string='Registro di registrazione',
        required=False,)
    """

    
    receivable_account_id = fields.Many2one(
        'account.account', string='Conto credito', required=False,
        help='Conto di credito del condominio')
    

    """
    payable_account_id = fields.Many2one(
        'account.account', string='Conto debito', required=True,
        help='Conto di debito del condominio')
    """

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

    @api.model
    def action_accounting(self):
        #Azione per gestire la contabilità dei condomini.
        view_id = self.env.ref('view_account_condominium_accounting').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contabilità condominio',
            'res_model': 'account.condominio',
            'view_mode': 'tree,form',
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
            ('code', '=', '2000'),
        ], limit=1)

        # Imposta il conto di debito del condominio.
        record.payable_account_id = self.env['account.account'].search([
            ('code', '=', '2100'),
        ], limit=1)
    
        #Crea un nuovo condominio.
        record = super(GcondAccountCondominium, self).create(vals)

        # Imposta la tipologia di registrazione di default.
        record.type_registration = 'debit'

        return record
    """

    
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
        