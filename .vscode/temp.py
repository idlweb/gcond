 # Controlla se il condominio è cambiato
            if self.condominio_id != self.condominio_id_old:
                 
            
                # Ottieni tutte le righe di dettaglio
                dettagli = self.env['account.condominio.table'].search([ ( 'table_id', '=', self.parte_numerica(str(self.id)) ) ])
                _logger.info('verifica esistenza dettagli:')
                _logger.info('=============INIZIO===================')
                _logger.info(self.id) 
                _logger.info('^^^^^')

                # Memorizza gli ID delle righe di dettaglio
                id_dettagli = {dettaglio.id for dettaglio in dettagli}
                
                #_logger.debug('')

                # Elimina tutte le righe di dettaglio
                for dettaglio_id in id_dettagli:
                    dettaglio = self.env['account.condominio.table'].browse(dettaglio_id)                
                    dettaglio.unlink()
                    
                _logger.info(list(id_dettagli))    
                _logger.info('==============FINE=================')
                
                # Esegui una commit manuale
                self.flush()
                 
                                                                            
                # Ripopola le righe di dettaglio
                condomini = self.env['res.partner'].search([('condominio_id', '=', self.condominio_id.id)])
                for condomino in condomini:
                    record = self.env['account.condominio.table'].create({
                        'table_id': self.id,
                        'condomino_id': condomino.id,
                        'quote' : 100.99,
                    })

           

            # Memorizza il valore corrente del condominio_id
            self.condominio_id_old = self.condominio_id


