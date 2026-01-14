# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Gcond',
    'version' : '18.0.1.2.0',
    'summary': 'Invoices & Payments',
    'sequence': 10,
    'description': """
        gcond -> Gestione condominiale
    """,
    'category': 'Accounting/Gestione_Condominio',
    'author': 'Vangi & Bard ',
    'website': 'https://www.odoo.com/app/invoicing',
    'images' : ['images/accounts.jpeg','images/bank_statement.jpeg','images/cash_register.jpeg','images/chart_of_accounts.jpeg','images/customer_invoice.jpeg','images/journal_entries.jpeg'],
    'depends' : [
        'web', 
        'website', 
        'base', 
        'account', 
        'crm', 
        'l10n_it',
        # OCA Financial (Verified)
        'account_financial_report',
        'account_asset_management',
        
        # OCA Financial (Pending/Unverified in 18.0)
        # 'l10n_it_withholding_tax',
        # 'account_financial_amount_check',
        # 'l10n_it_full_audit',
        # 'l10n_it_rea',
        # 'l10n_it_pec_itp',
        # 'account_reconciliation_widget',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_account_view.xml',
        'views/account_condominium_table_view.xml',
        'views/account_condominium_view.xml',
        'views/account_condomino_view.xml',
        'views/account_move_form_btn.xml',
        'views/account_sensore.xml',
        'views/account_payment_notice_view.xml',
        'views/menu.xml',
        'views/templates.xml',
        'views/condominio_banca.xml',
        'views/bilancio_view.xml',
        'reports/report_payment_receipt.xml',
        'reports/report_bilancio.xml',
        'reports/report_riparto.xml',
        'reports/report_patrimoniale.xml',
        'wizard/fee_wizard_view.xml',
        'data/sequence_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://unpkg.com/chart.js@2.8.0/dist/Chart.bundle.js',
            'https://unpkg.com/chartjs-gauge@0.3.0/dist/chartjs-gauge.js',
            'gcond/static/src/components/gauge_field/gauge_field.js',
            'gcond/static/src/components/gauge_field/gauge_field.xml',
            'gcond/static/src/views/m2m_group/m2m_group_controller.js',
            'gcond/static/src/views/m2m_group/m2m_group_renderer.js',
            'gcond/static/src/views/m2m_group/m2m_group.xml',
            'gcond/static/src/views/m2m_group/m2m_group_view.js',
            # Legacy files removed
        ],
        'web.assets_qweb': [
            # 'gcond/static/src/xml/qweb_template.xml', # Legacy - checking if still needed for M2m
        ],
    },    
    'demo': [
        #'demo/account_demo.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}