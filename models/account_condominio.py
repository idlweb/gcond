"""
    questa tabella rappresenta il condominio
    TO-DO: erediterà da res.partner e non da account.
    In odoo account.account rappresenta il piano dei conti
"""
from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)
import pdb
import random
import string

class GcondAccountCondominium(models.Model):
    _name = 'account.condominio'



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

    
   
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country',
        required=False)
   
    
    receivable_account_id = fields.Many2one(
        'account.account', string='Conto credito', required=False,
        help='Conto di credito del condominio')
    

    payable_account_id = fields.Many2one(
        'account.account', string='Conto debito', required=False,
        help='Conto di debito del condominio')
    

     
    """
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

    def replace_spaces_name_condominio(self, name):
        # Sostituiamo gli spazi con i trattini medi.
        new_name = name.replace(' ', '-')
        return new_name


    def has_journal(self, id):
        # Otteniamo il record del journal.
        journal = self.env['account.journal'].search([
            ('condominio_id', '=', id),
        ])

        # Se il record del journal è presente, allora il condominio ha già un journal.
        return journal


    def _generate_code(self):
        code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        while self.env['account.journal'].search([('code', '=', code)]):
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        return code


    def create_journal(self, name, id):
        # Creiamo il record del journal.
        if not self.has_journal(id):
            type_list = ['general', 'bank', 'cash']
            
            # Incrementiamo il valore del campo code.
            for index, type in enumerate(type_list):
                code = self._generate_code()  #'CO' + str(index + 1)

                if not self.env['account.journal'].check_code(code):
                    raise ValueError('Il codice del giornale deve essere univoco.')

                journal = self.env['account.journal'].create([{
                    'name': 'Condominio-'+self.replace_spaces_name_condominio(name)+type,
                    'code': code,
                    'type': type, #'general',
                    'condominio_id': int(id),
                }])        
    

        return journal
    
   
       
    @api.model
    def create(self, vals):
        #Crea un nuovo condominio.
        record = super(GcondAccountCondominium, self).create(vals)

        """
            Qui la logica dovrebbe essere quella di assegnare un conto di default
            che dovrebbe essere creato - ma potrebb essere inutile. Ho comunque 
            provato ad utilizzare la funzione create la scrittura con json
        """
        id = record.id
        self.create_journal(vals['name'], id)

        # Imposta il conto di credito del condominio.
        record.receivable_account_id = self.env['account.account'].search([
            ('code', '=', '250100'),
        ], limit=1)

        # Imposta il conto di debito del condominio.
        record.payable_account_id = self.env['account.account'].search([
            ('code', '=', '250100'),
        ], limit=1)
    
        """ 
        #Crea un nuovo condominio.
        record = super(GcondAccountCondominium, self).create(vals)
        La funzione crea, già sovrascrive il comportamento della creazione del nuovo record
        non c'è bisogno di richiamare ulteriormente lo stesso metodo
        """
        

        # Imposta la tipologia di registrazione di default.
        """ capire il senso di questa istruzione"""
        #record.type_registration = 'debit'

        return record
    

    """
        Seri dubbi che questo metodi funzioni    
    """
    def open_journal_view(self):
        # Otteniamo il record del condominio.
        condominio = self
        # Apri la vista account.journal.
        view = self.env['ir.ui.view'].search([
            ('model', '=', 'account.journal'),
            ('name', '=', 'Journals Condominii'),
        ])[0]
        # Imposta il filtro per condominio.
        view.domain = [('condominio_id', '=', condominio.id)]
        # Apri la vista.
        self.open_view(view)
        return None
    

    def _register_menus(self):
        # Aggiungiamo una voce di menu al modulo.
        menu = self.env['ir.ui.menu'].create({
            'name': 'Contabilita',
            #'parent_id': self.env.ref('account.menu_action_account_journal_tree').id,
            'parent_id': self.env.ref('gcond.menu_root').id,
            #'action': 'account.action_account_journal_tree',
            'action': 'open_journal_view',
        })
        return None


    def _post_init(self):
        # Aggiungiamo una voce di menu al modulo.
        self._register_menus()


    #@api.multi
    def distribute_charges(self, amount, table, document_number, account_id):
        charges = {}  
        """
            We are in the place where we must distribute for each 
            'condomino'? I think that 
        """                    
        #for condomino in self.related_condominiums: ## TO-DO resolve 'related_condominium' not exist! We have condominio_id
        for condomino in self.env['res.partner'].search([('condominio_id', '=', self.id)]):    
            # Get the condominium's share of the charge.
            # at this time 'table' contiene tutte le righe della tabella
            # account.condominio.table aventi lo stesso codice
            """
                TO-DO: nella maschera di registrazine alla pressione del bottone ripartisci 
                       spese o comunque all'esecuzione dell'action occorre una funzione che 
            """
            share = table.get(condomino.code_table) ## what get() do? 
            if share is None:
                # The condominium is not included in the distribution table.  ## what it meanning?
                continue

            # Calculate the condominium's charge.
            charge = amount * share

            # Create a journal entry for the charge.
            """
                Which is the difference between 'account_id: condominium.account_id.id' and 
                'account_id: condominium.account_id'
            """
            account_move = self.env['account.move'].create({
                'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
                'date': fields.Date.today(),
                'line_ids': [
                    {                        
                        'account_id': condomino.account_id.id, # credo ci sia fonfusione sulle entità in campo                                                        
                        'name': condomino.name,
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
            charges[condomino] = charge

        return charges
        