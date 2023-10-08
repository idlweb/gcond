from odoo import models, fields, api
"""
            D A   A P P R O F O N D I R E  !
There is a shortcut for this inheritance delegation. Instead of creating an _inherits
dictionary, you can use the delegate=True attribute in the Many2one field definition. 
This will work exactly like the _inherits option
"""

class LibraryMember(models.Model):
    _name = 'library.member'
    partner_id = fields.Many2one('res.partner', 
    ondelete='cascade', delegate=True)
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')

"""
Using abstract models for reusable model features 147
A noteworthy case of delegation inheritance is the users model, res.users. It inherits 
from partners (res.partner). This means that some of the fields that you can see on 
the user are actually stored in the partner model (notably, the name field). When a new 
user is created, we also get a new, automatically created partner.
"""