"""

Funzione su cui sto lavorando. 
Cancellazione di un recordset di dettaglio

   @api.onchange('condominio_id')
    def onchange_condominio_id(self):
        _logger.info('==============DEBUG=================3') 
        _logger.info('^^^^^^^^^^^^^^^^^il valore di condominio fuori è %s', self.condominio_id)
        if not self.condominio_id:
             pass
            # Se il condominio_id non è impostato, disabilitiamo la funzione onchange
        else:
            if self.condominio_id != self._origin.condominio_id or self.condominio_id == self._origin.condominio_id:  
                    # _origin è il valore precedente, condominio_id il new                    
                _logger.info('il valore di condominio è %s, quello precedente è %s', self.condominio_id, self._origin.condominio_id)
                condomini = self.env['res.partner'].search([('condominio_id.id', '=', self.condominio_id.id)])
            
                self.write({'table_ids': []})    
                self.table_ids = []
                self.table_ids.unlink()
                self.flush()
                # Ripopola le righe di dettaglio
                
                self.update({
                    'condominio_id': self.condominio.id,
                    }) 
                
                _logger.info('valore di condominio è %s', self.condominio_id)

                for condomino in condomini:
                    record = self.env['account.condominio.table'].create({
                        'table_id': self.id,
                        'condomino_id': condomino.id,
                        'quote' : 100.01,
                    })

            
        #self.write({'condominio_id_old': 999})
        #self.condominio_id_old = self.condominio_id 
        #self.flush()
        

        return {}

"""
           



dettagli = self.env['account.condominio.table'].search([ ( 'table_id', '=', self.parte_numerica(str(self.id)) ) ])
id_dettagli = {dettaglio.id for dettaglio in dettagli}

dettaglio = self.env['account.condominio.table'].browse(dettaglio_id)    

condomini = self.env['res.partner'].search([('condominio_id', '=', self.condominio_id.id)])

""" 
Interessante
"""
# Crea una lista dei record da cancellare.
record_da_cancellare = []
for record in self:
    # Verifica se il record è duplicato.
    if record.table_id.id in record.table_ids:
        record_da_cancellare.append(record.id)
self.env["account.condominio.table.line"].search([("id", "in", record_da_cancellare)]).unlink()


[(record.id, f'Condominio {record.condominio_id}') for record in self]


self.write({'campo_ids': [(6, 0)]})                       # il campo ids è stato aggiornato con una lista vuota


self.write({'campo_ids': [(record.id, 0) for record in self.campo_ids]})


self.update({
        'date_release': fields.Datetime.now(),
        'another_field': 'value'
         ...
        
 all_books.filter(lambda b: len(b.author_ids) > 1)        # quando si userebbe?

=================================================== GUIDA ==============================================================

Le tuple utilizzate con la funzione write() consentono di specificare le operazioni da eseguire sui campi di un record.

La prima tupla, (0, 0, dict_val), viene utilizzata per impostare il valore di un campo. La prima posizione della tupla, 0, 
indica che si sta eseguendo un'operazione di modifica (write()). La seconda posizione della tupla, 0, indica che non 
si sta eseguendo alcuna operazione di cancellazione (unlink()). La terza posizione della tupla, dict_val, è un dizionario 
che contiene le nuove impostazioni del campo.
Ad esempio, la seguente riga di codice imposta il valore del campo nome a Mario Rossi:

Python
self.write((0, 0, {'nome': 'Mario Rossi'}))

La seconda tupla, (1, id, dict_val), viene utilizzata per impostare il valore di un campo per un record specifico. 
La prima posizione della tupla, 1, indica che si sta eseguendo un'operazione di modifica (write()) su un record specifico. 
La seconda posizione della tupla, id, è l'ID del record su cui si sta eseguendo l'operazione. La terza posizione 
della tupla, dict_val, è un dizionario che contiene le nuove impostazioni del campo.
Ad esempio, la seguente riga di codice imposta il valore del campo nome a Mario Rossi per il record con ID 10:

Python
self.write((1, 10, {'nome': 'Mario Rossi'}))

La terza tupla, (2, id), viene utilizzata per cancellare un record specifico. La prima posizione della tupla, 2, 
indica che si sta eseguendo un'operazione di cancellazione (unlink()) su un record specifico. 
La seconda posizione della tupla, id, è l'ID del record da cancellare.
Ad esempio, la seguente riga di codice cancella il record con ID 10:

Python
self.write((2, 10))

La quarta tupla, (3, id), viene utilizzata per cancellare un campo specifico da un record specifico. 
La prima posizione della tupla, 3, indica che si sta eseguendo un'operazione di cancellazione (unlink()) 
di un campo specifico da un record specifico. La seconda posizione della tupla, id, è l'ID del record 
da cui si sta cancellando il campo.
Ad esempio, la seguente riga di codice cancella il campo nome dal record con ID 10:

Python
self.write((3, 10, 'nome'))

La quinta tupla, (4, id), viene utilizzata per aggiungere un record a un campo di tipo many2many. 
La prima posizione della tupla, 4, indica che si sta eseguendo un'operazione di aggiunta (create()) 
di un record a un campo di tipo many2many. La seconda posizione della tupla, id, è l'ID del record 
da aggiungere al campo.
Ad esempio, la seguente riga di codice aggiunge il record con ID 10 al campo campo_ids:

Python
self.write((4, 10, 'campo_ids'))

La sesta tupla, (5, id), viene utilizzata per rimuovere un record da un campo di tipo many2many. 
La prima posizione della tupla, 5, indica che si sta eseguendo un'operazione di rimozione (unlink()) 
di un record da un campo di tipo many2many. La seconda posizione della tupla, id, 
è l'ID del record da rimuovere dal campo.
Ad esempio, la seguente riga di codice rimuove il record con ID 10 dal campo campo_ids:

Python
self.write((5, 10, 'campo_ids'))

La settima tupla, (6, 0, id_list), viene utilizzata per aggiornare il valore di un campo di tipo many2many. 
La prima posizione della tupla, 6, indica che si sta eseguendo 
un'operazione di aggiornamento (write()) di un campo di tipo many2many. 
La seconda posizione della tupla, 0, indica che non si sta eseguendo alcuna operazione 
di cancellazione (unlink()). La terza posizione della tupla, id_list, 
è una lista di ID dei record da aggiungere o rimuovere dal campo.
Rimuovere:
self.write((6, 0, [10], 'category_ids'))