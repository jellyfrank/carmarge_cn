# -*- coding: utf-8 -*-
{
    'name': "Carmarge Stock China",

    'summary': """
        Carmarge Stock China
    """,

    'description': """
       Carmarge Stock China
    """,

    'author': "Kevin Kong",
    'website': "http://www.odoomommy.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'stock',
    'version': '14.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','carmarge_sale_cn'],

    # always loaded
    'data': [
        'security/data.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
