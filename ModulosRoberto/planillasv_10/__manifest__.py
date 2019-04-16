# -*- coding: utf-8 -*-
{
    'name': "planillasv_10",

    'summary': """
        Localización de El Salvador de la nomina,""",

    'description': """
        Localización de El Salvador de la nomina
    """,

    'author': "Strategi-k",
    'website': "http://www.strategi-k.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_contract','hr_payroll'],

    # always loaded
    'data': [
        'views/planilla.xml',
        'views/hr_employee.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
