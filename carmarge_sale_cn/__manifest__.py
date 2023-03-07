# -*- coding: utf-8 -*-
{
    'name': "Carmarge Sale Cn",

    'summary': """
        Carmarge Sale for China Business.
    """,

    'description': """
        Carmarge Sale for China Business.
    """,

    'author': "Kevin Kong",
    'website': "http://www.odoomommy.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '14.1',

    # any module necessary for this one to work correctly
    'depends': ['carmarge_purchase_cn','sale','sale_margin'],

    # always loaded
    'data': [
        'security/data.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/layout.xml',
        'views/templates.xml',
        'views/report.xml',
        'views/sale_order_views.xml',
        'views/account_report.xml',
        'views/account_report_templates.xml',
        'views/res_company_views.xml',
        'views/account_move_views.xml',
        'views/commercial.xml',
        'views/stock_report.xml',
        'views/product.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "qweb": [
        'static/src/xml/template.xml',
    ],
}
