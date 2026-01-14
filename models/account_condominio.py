"""
    questa tabella rappresenta il condominio
    TO-DO: erediterà da res.partner e non da account.
    In odoo account.account rappresenta il piano dei conti
    ????
"""
from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)

import random
import string

class GcondAccountCondominium(models.Model):
    _name = 'account.condominio'
    _description = 'Condominio'
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
    
    partner_id = fields.Many2one(
        'res.partner', string='Contatto Condominio', ondelete='restrict',
        help='Il contatto (res.partner) associato a questo condominio')
    
    child_ids = fields.One2many(
        related='partner_id.child_ids',
        string='Contatti Residenti')
    


    def replace_spaces_name_condominio(self, name):
        # Sostituiamo gli spazi con i trattini medi.
        # possibili ulteririori rimaneggiamenti
        new_name = name.replace(' ', '-')
        new_name = name.replace(',', '-')
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
            type_list = ['general', 'bank', 'cash','purchase']
            
            # Incrementiamo il valore del campo code.
            for index, type in enumerate(type_list):
                code = self._generate_code()  #'CO' + str(index + 1)
                journal = self.env['account.journal'].create([{
                    'name': 'Condominio-'+self.replace_spaces_name_condominio(name)+'-'+type,
                    'code': code,
                    'type': type, #'general',
                    'condominio_id': int(id),
                }])        
    
 
        return journal
    
   
       
    @api.model_create_multi
    def create(self, vals_list):
        # Crea nuovi condomini.
        records = super(GcondAccountCondominium, self).create(vals_list)
        for record in records:
            # Crea il partner associato
            partner_vals = {
                'name': record.name,
                'is_company': True,
                'street': record.address,
                'city': record.city,
                'zip': record.zip,
                'country_id': record.country_id.id,
                'phone': record.phone,
                'email': record.email,
                'vat': record.vat,
                'company_type': 'company',
                'is_condominio': True,
            }
            partner = self.env['res.partner'].create(partner_vals)
            record.partner_id = partner.id
            
            self.create_journal(record.name, record.id)
        return records

    def write(self, vals):
        res = super(GcondAccountCondominium, self).write(vals)
        # Sincronizza i dati con il partner associato
        partner_fields = {
            'name': 'name',
            'address': 'street',
            'city': 'city',
            'zip': 'zip',
            'country_id': 'country_id',
            'phone': 'phone',
            'email': 'email',
            'vat': 'vat',
        }
        partner_vals = {}
        for cond_field, partner_field in partner_fields.items():
            if cond_field in vals:
                # Se è un Many2one, prendiamo l'id (che è già in vals come intero)
                partner_vals[partner_field] = vals[cond_field]

        if partner_vals:
            for record in self:
                if record.partner_id:
                    record.partner_id.write(partner_vals)
        return res
    
    
    def create_cost_items_for_condominio(self):
        # Ottieni l'id del condominio.
        condominio_id = self.id

        """
            ma esiste una tabella delle voci di costo?
        """

        # Questa tabella è inesistente
        cost_items = self.env['account.cost.item'].search([])

        # Per ogni voce di costo esistente:
        for cost_item in cost_items:
            # Crea una nuova voce di costo.
            new_cost_item = self.env['account.cost.item'].create({
                'name': cost_item.name,
                'description': cost_item.description,
                'condominio_id': condominio_id,
            })

            # Imposta l'id del condominio come valore del campo `condominio_id` della nuova voce di costo.
            new_cost_item.condominio_id = condominio_id

    #=================================================================================================

    """
        Seri dubbi che questo metodo funzioni    
    """
    def action_view_journal_entries(self):
        self.ensure_one()
        # Trova tutti i giornali associati a questo condominio
        journals = self.env['account.journal'].search([('condominio_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': f'Movimenti Contabili: {self.name}',
            'res_model': 'account.move.line',
            'view_mode': 'list,form',
            'domain': [('journal_id', 'in', journals.ids)],
            'context': dict(self.env.context, search_default_journal_id=journals.ids[0] if journals else False),
        }

    def open_journal_view(self):
        # Manteniamo per compatibilità con i menu esistenti
        self.ensure_one()
        return self.action_view_journal_entries()
    
    def action_view_customer_aging_condominio(self):
        """
        Shows the 'Morosità' (Debts of Residents) for this specific Condo.
        Uses res.partner.aging.customer view.
        """
        self.ensure_one()
        # 1. Refresh View
        self.env['res.partner.aging.customer'].execute_aging_query(
            age_date=fields.Date.context_today(self)
        )
        
        # 2. Open filtered by partners belonging to this condo
        # Logic: We filter the Agings where partner_id.condominio_id = self.id
        return {
            'type': 'ir.actions.act_window',
            'name': f'Morosità: {self.name}',
            'res_model': 'res.partner.aging.customer',
            'view_mode': 'list',
            'domain': [
                ('partner_id.condominio_id', '=', self.id),
                ('total', '!=', 0)
            ],
            'context': self.env.context,
        }

    def action_view_supplier_aging_condominio(self):
        """
        Shows the 'Scadenziario Fornitori' (Debts TO Suppliers) for this Condo.
        Uses res.partner.aging.supplier view.
        """
        self.ensure_one()
        # 1. Refresh View
        self.env['res.partner.aging.supplier'].execute_aging_query(
            age_date=fields.Date.context_today(self)
        )
        
        # 2. Open filtered. 
        # Suppliers don't belong to the condo, but the INVOICES do.
        # The View 'res.partner.aging.supplier' has 'invoice_id'.
        # We can filter by invoice_id.journal_id.condominio_id
        return {
            'type': 'ir.actions.act_window',
            'name': f'Scadenziario Fornitori: {self.name}',
            'res_model': 'res.partner.aging.supplier',
            'view_mode': 'list',
            'domain': [
                ('invoice_id.journal_id.condominio_id', '=', self.id),
                ('total', '!=', 0)
            ],
            'context': self.env.context,
        }
    

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



