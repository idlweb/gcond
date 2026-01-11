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
    _description = 'Tabella di Ripartizione Master'

    name = fields.Char(string='Name', required=True)
    code_table = fields.Char(string='Codice tabella')
    description = fields.Char(string='Descrizione')
    expense_type_id = fields.Many2one(
        'gcond.expense.type',
        string='Tipo di Spesa',
        help='Tipologia di spesa gestita da questa tabella (es. Acqua, Riscaldamento).',
        required=True
    )
    
    condominio_id = fields.Many2one(
        'account.condominio',
        string='Condominio',
        required=True
    )
    # account_ids removed in favor of expense_type_id architecture

    _sql_constraints = [
        ('unique_expense_type_per_condominio', 
         'unique(condominio_id, expense_type_id)', 
         'Può esistere una sola tabella di ripartizione per questo tipo di spesa in questo condominio!')
    ]
    
    percentuale = fields.Float(string='Percentuale da ripartire', default=100.0)
    table_ids = fields.One2many('account.condominio.table', 'table_id', string='Righe tabelle condominiali')
    
    #condominio_id_old = fields.Integer(string='Condominio ID vecchio')
    
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



    @api.onchange('condominio_id')
    def onchange_condominio_id(self):
        if not self.condominio_id:
            self.table_ids = [(5, 0, 0)]
            return
            
        # Trova tutti i partner associati al condominio scelto
        condomini = self.env['res.partner'].search([('condominio_id', '=', self.condominio_id.id)])
        
        lines = []
        for condomino in condomini:
            lines.append((0, 0, {
                'condomino_id': condomino.id,
                'quote': 100.0,
            }))
        
        # Pulisce le righe esistenti e aggiunge i nuovi condomini
        self.table_ids = [(5, 0, 0)] + lines
        return {}


    