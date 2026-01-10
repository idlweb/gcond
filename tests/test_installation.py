from odoo.tests.common import TransactionCase

class TestGcondInstallation(TransactionCase):

    def test_create_condominio(self):
        """ Test creating a account.condominio record to verify module installation """
        condominio = self.env['account.condominio'].create({
            'name': 'Test Condominio',
            'code': 'TEST1',
            'vat': 'IT12345678901',
            'city': 'Roma',
            'zip': '00100',
        })
        self.assertTrue(condominio.id)
