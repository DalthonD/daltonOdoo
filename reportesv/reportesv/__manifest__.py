# -*- coding: utf-8 -*-
{
    'name': "Reporte-SV",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': "Creación de Reportes para Compras, Ventas Contribuyentes y  Ventas Consumidores"
        "Long description of module's purpose",

    'author': "strategiksv",
    'website': "http://Strategi-k.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Reporting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','purchase','account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_report_pdf_view.xml',
        '',

    ],
    # only loaded in demonstration mode
    'qweb': [,
    ],
}
