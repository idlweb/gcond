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
    'depends' : ['web','website','base','account'],
    'data': [
        'data/sequence_data.xml',
        'security/ir.model.access.csv',
        'views/account_condominium_table_view.xml',
        'views/account_condominium_view.xml',
        'views/account_condomino_view.xml',
        'views/account_move_form_btn.xml',
        'views/account_sensore.xml',
        'views/menu.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://unpkg.com/chart.js@2.8.0/dist/Chart.bundle.js',
            'https://unpkg.com/chartjs-gauge@0.3.0/dist/chartjs-gauge.js',
            'gcond/static/src/js/gauge_widget.js',
            'gcond/static/src/css/gauge_widget.scss',
            'gcond/static/src/js/m2m_group_view.js',
            'gcond/static/src/js/m2m_group_model.js',
            'gcond/static/src/js/m2m_group_controller.js',
            'gcond/static/src/js/m2m_group_renderer.js',
        ],
        'web.assets_qweb': [
            'gcond/static/src/xml/qweb_template.xml',
        ],
    },    
    'demo': [
        #'demo/account_demo.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}