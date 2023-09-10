# Modulo: condominio
# File: tabelle_ripartizione.py

from odoo import models, fields, api


class TabelleRipartizione(models.Model):
    _name = "condominio.tabelle_ripartizione"

    # Descrizione

    descrizione = fields.Char(string="Descrizione")

    # Tipologia

    tipologia = fields.Selection(
        [("superficie", "Superficie"), ("numero_unita_immobiliare", "Numero unità immobiliare")],
        string="Tipologia",
    )

    """
    # Quote di partecipazione
    quote_di_partecipazione = fields.One2many(
        "condominio.quote_di_partecipazione", "tabella_ripartizione_id", string="Quote di partecipazione"
    )
    """