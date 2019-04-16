# -*- coding: utf-8 -*-
{
    'name': "strategikcrm",

    'summary': """
        Modificaciones al CRM para los clientes de Strategi-K,""",

    'description': """
        Contiene las modificaciones realizadas por Strategi-K para su clientes.
        Formatos de presupuestos
        Campos adicionales en la ficha de clientes
    """,

    'author': "strategi-k",
    'website': "http://www.strategik.com.sv",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
