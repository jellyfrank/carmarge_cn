# -*- coding: utf-8 -*-
{
    'name': "Caramarge Account China",

    'summary': """
        Carmarge Acount China
    """,

    'description': """
        Carmarge Acount China
    """,

    'author': "Kevin Kong",
    'website': "http://www.odoomommy.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'tools',
    'version': '14.1',

    # any module necessary for this one to work correctly
    'depends': ['carmarge_product_cn'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    "qweb": [
        # 'static/src/xml/template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
