from odoo import models, fields, api
"""
1. Add the many-to-one field for the book's publisher to Library Books:
"""
class LibraryBook(models.Model): 
    # ... 
    publisher_id = fields.Many2one(     
    'res.partner',                              ### tabella MASTER
    string='Publisher', 
    # optional: 
    ondelete='set null', 
    context={}, 
    domain=[], 
)

"""
2. To add the one-to-many field for a publisher's books, we need to extend the partner 
model. For simplicity, we will add that to the same Python file:
"""

class ResPartner(models.Model): 
    _inherit = 'res.partner' 
    published_book_ids = fields.One2many( 
    'library.book',                             ### Tabella DETAIL
    'publisher_id',                             ### campo detto "CHIAVE ESTERNA"
    string='Published Books') 

"""
The _inherit attribute we use here is for inheriting an existing model. This will 
be explained in the Adding features to a model using inheritance recipe later in this 
chapter.
3. We've already created the many-to-many relation between books and authors, but 
let's revisit it:
"""

class LibraryBook(models.Model): 
    # ... 
    author_ids = fields.Many2many( 
    'res.partner', string='Authors')            ### posso associare più id di un'altra tabella

"""
4. The same relation, but from authors to books, should be added to the partner 
model:
"""

class ResPartner(models.Model): 
    # ... 
    authored_book_ids = fields.Many2many( 
    'library.book',                             ### vista dall'altra parte :-) 
    string='Authored Books', 
    # relation='library_book_res_partner_rel' -> optional (se avessi bisogno di esplicitare la relazione che risolve il molti a molti) 
 ) 

"""

Abbiamo affrontato il modo più breve per definire i campi relazionali. Diamo un'occhiata agli 
attributi specifici di questo tipo di campo.

Gli attributi dei campi One2many sono i seguenti:
- comodel_name: è l'identificatore del modello di destinazione ed è obbligatorio per tutti i campi relazionali. 
  campi relazionali, ma può essere definito in base alla posizione, senza la parola chiave.
- inverse_name: si applica solo a One2many ed è il nome del campo nel modello di destinazione per l'inverso di Many2one. 
  per la relazione inversa Many2one.
- limit: si applica a One2many e Many2many e imposta un limite opzionale in termini di numero di record da leggere. 
  numero di record da leggere che vengono utilizzati a livello di interfaccia utente.

Gli attributi del campo Many2many sono i seguenti:
- comodel_name: è lo stesso del campo One2many.
- relation: Questo è il nome da utilizzare per la tabella che supporta la relazione, sovrascrivendo il nome 
  il nome definito automaticamente.
- column1: è il nome del campo Many2one nella tabella relazionale che si collega a questo modello. 
questo modello.
- colonna2: È il nome del campo Many2one della tabella relazionale che si collega al modello. 
comodel.

Per le relazioni Many2many, nella maggior parte dei casi, l'ORM si occuperà dei valori predefiniti di questi attributi. 
È persino in grado di rilevare le relazioni Many2many inverse, di individuare la tabella di relazioni già esistente e 
di invertire opportunamente i valori di column1 e column2.


"""