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
import pprint
import re


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
    
    #condominio_id_old = fields.Integer(string='Condominio ID vecchio')
    
    
    """
    @api.model
    def create(self, vals):
        return super(AccountCondominioTableMaster, self).create(vals)
    """ 

    """
    @api.onchange('state')
    def onchange_state(self):
        pass
    """

    """
    def create(self, vals):
        # Recupera il conto di contabilità di default per la tabella di ripartizione
        account_id = self.env['account.condominio.table.master'].search([('code_table', '=', vals['code_table'])], limit=1).account_id
        # Associa il conto di contabilità alla tabella di ripartizione
        vals['account_id'] = account_id
        #
        return super(AccountCondominioTableMaster, self).create(vals)
    """

  

    def parte_numerica(self,stringa):
        """
        Prende solo la parte numerica di una stringa.
        Args: stringa: La stringa da cui prendere la parte numerica.
        Returns: La parte numerica della stringa.
        """
        # Cerca un'espressione regolare che corrisponde a una stringa di numeri.
        match = re.match(r"\d+", stringa)

        # Se l'espressione regolare viene trovata, restituisce la parte numerica della stringa.
        if match:
            return match.group()
        else:
            return None


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

    
