# -*- coding: utf-8 -*-
{
    'name': "List Preview Widget",

    'summary': """
        List Preview Widget
    """,

    'description': """
        List Preview Widget
    """,

    'author': "Kevin Kong",
    'website': "http://www.odoomommy.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'tools',
    'version': '14.1',

    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'qweb':[
        'static/src/xml/list_preview.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
