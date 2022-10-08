# -*- coding: utf-8 -*-
{
    'name': "Mommy Base",

    'summary': """
        Basic feature powered by Odoomommy.com
    """,

    'description': """
        1. 支持指定计算字段分组汇总
        2. 个性化个人中心配置
        3. 基础模型支持当前活动记录
        4. 封装统一提示框
        5. 打印报表支持第二名称
    """,

    'author': "Kevin Kong",
    'website': "http://www.odoomommy.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'basic',
    'version': '14.3',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        "views/settings.xml",
        "views/pops.xml",
        'views/ir.xml'
    ],
    "qweb":[
        "static/src/xml/web.xml"
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
