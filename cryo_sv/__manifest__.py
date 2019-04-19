# -*- coding: utf-8 -*-

{
    "name": "CRYO SV",
    "category": 'Sales',
    "summary": """
       Localizacion de CRYO .""",
    "description": """
   Registra la orden de produccions y POS  para CRYO
    """,
    "sequence": 1,
    "author": "Strategi-k",
    "website": "http://strategi-k.com",
    "version": '12.0.0.5',
    "depends": ['sale','base','point_of_sale',],
    "data": [
        'security/ir.model.access.csv',
    'views/assets.xml',
    ],
    "qweb": ['static/src/xml/pos.xml'],
    "installable": True,
    "application": True,
    "auto_install": False,
}
