"""
1. Utilizzando il metodo self.mapped()
Il metodo self.mapped() è un metodo di campo che restituisce 
un elenco di record corrispondenti al valore di un campo.
In questo caso, possiamo utilizzare il metodo self.mapped() 
per ottenere un elenco di tutti i condomini di un condominio.
"""

def distribute_charges(self, amount, table, document_number, account_id):
    # Itera su tutti i condomini del condominio
    for condomino in self.mapped(' condominio_id'):
        pass

"""
2. Utilizzando il metodo self.search()
Il metodo self.search() è un metodo di classe che restituisce 
un elenco di record corrispondenti a un criterio di ricerca. 
In questo caso, possiamo utilizzare il metodo self.search() 
per ottenere un elenco di tutti i condomini di un condominio.

"""

def distribute_charges(self, amount, table, document_number, account_id):
    # Itera su tutti i condomini del condominio
    for condomino in self.search([('condominio_id', '=', self.id)]):
        pass

"""
3. Utilizzando il metodo self.env['res.partner'].search()
Il metodo self.env['res.partner'].search() è un metodo di ambiente 
che restituisce un elenco di record corrispondenti a un criterio di ricerca. 
In questo caso, possiamo utilizzare il metodo 
self.env['res.partner'].search() per ottenere 
un elenco di tutti i condomini di un condominio.
"""

def distribute_charges(self, amount, table, document_number, account_id):
    # Itera su tutti i condomini del condominio
    for condomino in self.env['res.partner'].search([('condominio_id', '=', self.id)]):
        pass

"""
4. Utilizzando il metodo self.env['account.condominio'].search()
Il metodo self.env['account.condominio'].search() è un metodo di ambiente
che restituisce un elenco di record corrispondenti a un criterio di ricerca. 
In questo caso, possiamo utilizzare il metodo self.env['account.condominio'].search() 
per ottenere un elenco di tutti i condomini di un condominio.
"""

def distribute_charges(self, amount, table, document_number, account_id):
    # Itera su tutti i condomini del condominio
    for condomino in self.env['account.condominio'].search([('id', 'in', self. condominio_id.ids)]):
        pass

"""
 
5. Utilizzando un ciclo for personalizzato
Possiamo anche utilizzare un ciclo for personalizzato per iterare su tutti i condomini di un condominio.
"""
def distribute_charges(self, amount, table, document_number, account_id):
    # Itera su tutti i condomini del condominio
    for condomino in self. condominio_id:
        pass