from odoo import models, fields, api


class Partner(models.Model):
    _inherit = "res.partner" 

    condomino_id = fields.Many2one(
        comodel_name='account.condomino',
        string='Condominio',
        ondelete='set null',
    )


    type_condomino = fields.Selection(
        [('affuttuario', 'Affittuario'), ('proprietario', 'Proprietario')],
        string='Tipologia condomino',
        default='proprietario',)


    """
    # fix many2many da 'estensione ereditaria'
    tax_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='account_condominio_tax_rel',
        column1='condominio_id',
        column2='tax_id',
        string='Taxes', 
    )
    """
    