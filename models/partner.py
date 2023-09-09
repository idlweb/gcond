from odoo import models, fields, api


class Partner(models.Model):
    _inherit = "res.partner"

    # Proprietario

    proprietario = fields.Boolean(string="Proprietario")

    # Tabella di Ripartizione

    tabella_ripartizione_id = fields.Many2one(
        "condominio.tabelle_ripartizione", string="Tabella di Ripartizione"
    )