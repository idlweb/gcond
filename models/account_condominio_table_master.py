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

    @api.onchange('condominio_id')
    def onchange_condominio_id(self):
        
        self.name = 'prova'
        self.table_ids = []

        _logger.info('==============DEBUG=================5') 
        _logger.info('^^^^^^^^^^^^^^^^^il valore di condominio fuori è %s', self.condominio_id)
        
        if not self.condominio_id:
             pass
            # Se il condominio_id non è impostato, disabilitiamo la funzione onchange
        else:
            if self.condominio_id != self._origin.condominio_id:  
               
                # _origin è il valore precedente, condominio_id il new                    
                _logger.info('il valore di condominio è %s, quello precedente è %s', self.condominio_id, self._origin.condominio_id)
                
               
            
            
        #self.write({'condominio_id_old': 999})
        #self.condominio_id_old = self.condominio_id 
        #self.flush()
        #
        """
        result = { 
            'name': "TESTO", 
            'description': "sto scrivendo dopo", 
            'code_table': self.code_table,
            'account_id': self.account_id,
            'condominio_id': self.condominio_id
            #'domain': {'table_ids': [ 
            #            ('id', 'in', self.table_ids.ids)] 
            #        } 
        } 
        message = ('La somma non deve superare 1000:\n') 
        #titles = late_books.mapped('book_id.name') 
        """
        """
        result['warning'] = { 
            'title': 'misure', 
            'message': message #+ '\n'.join(titles) 
        }  
        """
        return []

   