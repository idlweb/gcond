# Modulo: condominio
# File: quote_di_partecipazione.py

from odoo import models, fields, api


class QuoteDiPartecipazione(models.Model):
    _name = "gcond.quote_di_partecipazione"

    # Tabella di Ripartizione

    tabella_ripartizione_id = fields.Many2one(
        "gcond.tabelle_ripartizione", string="Tabella di Ripartizione"
    )

    # Condomino

    condomino_id = fields.Many2one(
        "res.partner", string="Condomino", domain="[('proprietario', '=', True)]"
    )

    # Quota di partecipazione

    quota_di_partecipazione = fields.Float(string="Quota di partecipazione")