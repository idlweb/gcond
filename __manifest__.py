# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Gcond',
    'version' : '1.2',
    'summary': 'Invoices & Payments',
    'sequence': 10,
    'description': """
        gcond -> Gestione condominiale
    """,
    'category': 'Accounting/Gestione_Condominio',
    'author': 'Vangi & Bard ',
    'website': 'https://www.odoo.com/app/invoicing',
    'images' : ['images/accounts.jpeg','images/bank_statement.jpeg','images/cash_register.jpeg','images/chart_of_accounts.jpeg','images/customer_invoice.jpeg','images/journal_entries.jpeg'],
    'depends' : ['account'],
    'data': [
        #'security/account_security.xml',
        #'security/ir.model.access.csv',
        #'data/account_data.xml',
        #'data/digest_data.xml',
        #'views/account_report.xml',
        'account_condominium_table_view.xml',
        'account_condominium_view.xml',
        'account_move_form_btn.xml',
        'menu.xml',
    ],
    'demo': [
        #'demo/account_demo.xml',
    ],
    'installable': True,
    'application': True,
    #'post_init_hook': '_account_post_init',
    'license': 'LGPL-3',
}