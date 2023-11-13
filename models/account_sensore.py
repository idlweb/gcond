"""
    questa tabella rappresenta l'entità sensore
    TO-DO: per ora non ha eredi
    In odoo account.account rappresenta il piano dei conti
"""
from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)
import pdb
import random
import string

from pymodbus.client.tcp import ModbusTcpClient


class GcondAccountSensore(models.Model):
    _name = 'account.sensore'

    _description = 'Modello per la gestione dei sensori'

    # Campi

    categoria_sensore = fields.Char(string='Categoria sensore', required=True)
    nome = fields.Char(string='Nome', required=True)
    descrizione = fields.Char(string='Descrizione')
    protoc_trasf_dati = fields.Char(string='Protocollo di trasferimento dati')
    protoc_conn = fields.Char(string='Protocollo di connessione')
    res_partner_id = fields.Many2one('res.partner', string='Partner')
    progetto_id = fields.Many2one('project.project', string='Progetto')
    id_registro_plc = fields.Integer(string='ID registro PLC')
    slave_id = fields.Integer(string='ID slave')
    tipo_registro_plc = fields.Char(string='Tipo registro PLC')
    address_server = fields.Char(string='Indirizzo server')
    port_server = fields.Integer(string='Porta server')

    valore_bool = fields.Boolean(string='True-False',  default=True)
    valore_intero_interr = fields.Integer(string='Valore intero', compute='_compute_progressbar', default=100)
    valore_decimale_libero = fields.Float(string='Valore decimale')
    
    max_rate = fields.Integer(string='Maximun rate', default=100)

    # Relazioni

    partner = fields.Many2one('res.partner', string='Partner', related='res_partner_id', store=True)
    progetto = fields.Many2one('project.project', string='Progetto', related='progetto_id', store=True)

    #logica di business

    # Gestione interruttore con widget 'bar' -> <field name="grafico" widget="bar" />
    @api.depends('valore_bool')
    def _compute_progressbar(self): 
        self.valore_bool = self.read_value(self.id)      
        if self.valore_bool:
            progress = 100
            self.valore_intero_interr = progress
        else:
            progress = 0
            self.valore_intero_interr = progress
        return self.valore_intero_interr

    @api.model
    def connectServerModbus(self,id):
        sensore = self.env['account.sensore'].browse(id) 
        client = ModbusTcpClient(host="92.223.253.226", port=502, unit=10, debug=True)
        #client = GcondAccountSensore.ModbusClient(str(sensore.address_server), sensore.port_server, sensore.slave_id) 
        client.connect() 
        return client

    @api.model #approfondire l'utilizzo del model, mi sa che agisce non sul record ma sulla struttura
    def read_value(self, id):
        client = self.connectServerModbus(self.id)
        sensore = self.env['account.sensore'].browse(id) 
        value = client.read_coils(23, sensore.slave_id)
        sensore.valore_bool = value
        client.close()
        return value

    @api.model #approfondire l'utilizzo del model, mi sa che agisce non sul record ma sulla struttura
    def write_value_on(self, id):
        client = self.connectServerModbus(self.id)
        sensore = self.env['account.sensore'].browse(id) 
        value = client.write_coil(22, True, sensore.slave_id)
        sensore.valore_bool = value
        client.close()
        if value:
            return value
        return 1 
    
    @api.model
    def write_value_off(self, id):
        client = self.connectServerModbus(self.id)
        sensore = self.env['account.sensore'].browse(id) 
        value = client.write_coil(22, False, sensore.slave_id)
        sensore.valore_bool = value
        client.close()
        if value:
            return value
        return 1  

    """
        client.write_coil(22, True, slave=10)
        result = client.read_coils(22,1,slave=10)
        print(result.bits[0])
        client.close()
    """

    class ModbusClient:

        def __init__(self, host, port, unit):
            self.client = ModbusTcpClient(host, port, unit)

        def connect(self):
            self.client.connect()

        def read_coil(self, address, slave=1):
            result = self.client.read_coils(address, 1, slave)
            return result.bits[0]

        def write_coil(self, address, value, slave=1):
            result = self.client.write_coil(address, value, slave)
            return result.bits[0]

        def read_register(self, address, slave=1):
            result = self.client.read_holding_registers(address, 1, slave)
            return result.registers[0]
    
        
        
    """
        TO-DO:
        Questo snippet potrebbe essere inserito in una sorta di libreria 
        esterna al modello, altrimenti qui dovrei portarmi tutte le possibilità
        di connessione ed i parametri necessari. 
        Vero è che, quelle in uso, sono prevalentemente con modbus
        Per ora inerisco qui per velocizzare
    """

    