
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
    #table_ids = fields.One2many(comodel_name='account.condominio.table', string='Righe tabelle condominiali')
    
    

    @api.model
    def create(self, vals):
        return super(AccountCondominioTableMaster, self).create(vals)

    """
    def create(self, vals):
        # Recupera il conto di contabilità di default per la tabella di ripartizione
        account_id = self.env['account.condominio.table.master'].search([('code_table', '=', vals['code_table'])], limit=1).account_id
        # Associa il conto di contabilità alla tabella di ripartizione
        vals['account_id'] = account_id
        #
        return super(AccountCondominioTableMaster, self).create(vals)
    """

    def view_form(self, cr, uid, ids, context=None):
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
                    </group>
                  </sheet>   
                </form>
            """,
        }


    def view_tree(self, cr, uid, ids, context=None):
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

    