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
    account_ids = fields.Many2many('account.account',  string='Conti di contabilità')
    percentuale = fields.Float(string='Percentuale')
    color = fields.Integer()
    
    condominio_id = fields.Many2one(
        comodel_name='account.condominio',  
        string='Condominio di appartenenza',
    )
  
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
             pass
            # Se il condominio_id non è impostato, disabilitiamo la funzione onchange
        else:
            if self.condominio_id != self._origin.condominio_id:  
                # _origin è il valore precedente, condominio_id il new                    
                _logger.info('il valore di condominio è %s, quello precedente è %s', self.condominio_id, self._origin.condominio_id) 
                
                """
                # Utilizza il metodo per cancellare tutte le ricorrenze
                context_copy = self.env.context.copy()
                # Aggiorna la copia del context
                context_copy.update({'table_ids': []})
                # Aggiorna il context originale
                self.env.context = context_copy
                """

                self.write({'table_ids': []})
                self.table_ids = self.env.context.get('table_ids')                
                condomini = self.env['res.partner'].search([('condominio_id.id', '=', self.condominio_id.id)])               
                for condomino in condomini:
                    record = self.env['account.condominio.table'].create({
                        'table_id': self.id,
                        'condomino_id': condomino.id,
                        'quote' : 100,
                    })
            else:
                self.write({'table_ids': []})
                self.table_ids = self.env.context.get('table_ids')
                self.condominio_id = self._origin.condominio_id
                condomini = self.env['res.partner'].search([('condominio_id.id', '=', self.condominio_id.id)])                           
                for condomino in condomini:
                    record = self.env['account.condominio.table'].create({
                        'table_id': self.id,
                        'condomino_id': condomino.id,
                        'quote' : 100,
                    })
            
        return []


    