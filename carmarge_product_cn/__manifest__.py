# -*- coding: utf-8 -*-
{
    'name': "Carmarge Product",

    'summary': """
        Carmarge Product For China Business.
    """,

    'description': """
        Carmarge Product For China Business.
    """,

    'author': "Kevin Kong",
    'website': "http://www.odoomommy.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'product',
    'version': '14.1',

    # any module necessary for this one to work correctly
    'depends': ['delivery'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/product.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
