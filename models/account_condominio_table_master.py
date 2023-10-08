
"""
    questa tabella è il luogo in cui associo ad una 
    tabella di ripartizione la voce contabile di costo 
    corrispondete, dimodoche alla creazione della 
    registrazione contabile si possa facilitare sia la registrazione
    che la ripartizione.
    In odoo account.account rappresenta il piano dei conti
"""
from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)
import pdb


class AccountCondominioTableMaster(models.Model):
    _name = 'account.condominio.table.master'

    name = fields.Char(string='Name', required=True)
    code_table = fields.Char(string='Codice tabella')
    description = fields.Char(string='Descrizione')
    account_id = fields.Many2one('account.account', string='Conto di contabilità')
    condominio_id = fields.Many2one(
        comodel_name='account.condominio',  
        string='Condominio di appartenenza',
    )
  
    table_ids = fields.One2many('account.condominio.table', 'table_id', string='Righe tabelle condominiali')
    
    """
    @api.model
    def create(self, vals):
        return super(AccountCondominioTableMaster, self).create(vals)
    """

    @api.onchange('condominio_id')
    def onchange_condominio_id(self):
        # Ottieni tutti i condomini
        condomini = self.env['res.partner'].search([('condominio_id', '=', self.condominio_id.id)])

        # Crea un ciclo per ogni condomino
        for condomino in condomini:
            # Crea una nuova riga di dettaglio
            record = self.env['account.condominio.table'].create({
                'table_id': self.id,
                'condomino_id': condomino.id,
                'quote' : 100,
            })

        return {}
    
    @api.model
    def create(self):
        # Avvia la funzione onchange solo se il campo condominio_id è diverso da 0
        #if self.condominio_id:
        #    self.onchange_condominio_id()

        # Crea un ciclo per ogni condominio
        for condomino in self.condominio_id.partner_ids:
            # Crea una nuova riga di dettaglio
            record = self.env['account.condominio.table'].create({
                'table_id': self.id,
                'condomino_id': condomino.id,
                'quote' : 100,
            })

        return super(account_condominio_table_master, self).create()

        return super(AccountCondominioTableMaster, self).create()

    """
    def create(self, vals):
        # Recupera il conto di contabilità di default per la tabella di ripartizione
        account_id = self.env['account.condominio.table.master'].search([('code_table', '=', vals['code_table'])], limit=1).account_id
        # Associa il conto di contabilità alla tabella di ripartizione
        vals['account_id'] = account_id
        #
        return super(AccountCondominioTableMaster, self).create(vals)
    """


    """
        Per ora le def sulle actions dovrebbero funzionanare solo sui bottoni delle viste
    """
    def action_table_master_view_form(self, cr, uid, ids, context=None):
        return {
            'name': 'Inserisci tabella di ripartizione',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.condominio.table.master',
            'domain': [('id', 'in', ids)],
            'context': context,
            'fields': ['code_table', 'description', 'account_id'],
            'arch': """
                <form string="Inserisci tabella di ripartizione">
                  <sheet>
                    <group>
                        <field name="code_table" required="True"/>
                        <field name="description" required="True"/>
                        <field name="account_id" required="True"/>                 
                         <field name="details" widget="field.tree" relation="account.condominio.table" target="new">
                            <tree string="Dettaglio tabella di ripartizione">
                                <field name="table_id"/>
                                <field name="unit_of_measure" label="udm"/>
                                <field name="value_distribution" label="valore"/>
                                <field name="quote" label="%"/>                                                                
                            </tree>
                        </field>
                    </group>
                  </sheet>   
                </form>
            """,
        }


    def action_table_master_view_tree(self, cr, uid, ids, context=None):
        return {
            'name': 'Tabelle di ripartizione',
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'account.condominio.table.master',
            'domain': [('id', 'in', ids)],
            'context': context,
            'fields': ['id', 'code_table', 'description'],
            'arch': """
                <tree string="Tabelle di ripartizione">
                    <field name="code_table"/>
                    <field name="description"/>
                </tree>
            """,
    }

    