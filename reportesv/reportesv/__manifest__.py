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
    'depends': ['base','account','purchase','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/purchase_report.xml',
        'views/purchase_report_view.xml',
        'views/consumer_sales_report.xml',
        'views/consumer_sales_report_view.xml',
        'views/taxpayer_sales_report.xml',
        'views/taxpayer_sales_report_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [

    ],
}
