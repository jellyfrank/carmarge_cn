# -*- coding: utf-8 -*-
{
    'name': "Product History",

    'summary': """
        adding product history price into sale/purchase order.
    """,

    'description': """
        adding product history price into sale/purchase order.
    """,

    'author': "Kevin Kong",
    'website': "http://www.odoomommy.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'product',
    'version': '14.1',

    # any module necessary for this one to work correctly
    'depends': ['sale','purchase','list_preview_widget'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/data.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
