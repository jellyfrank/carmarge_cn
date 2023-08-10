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
        6. 支持表单视图标签颜色自定义
        7. 支持列表视图自定义样式
        8. 打印报表添加条件校验
        9. 字段添加UNIQUE属性,支持自定义提示文本
        10. 表单X2many字段树形控制分页设置
        11. 添加模型跟踪Track All功能
        12. qweb报表添加货币符号去除功能
    """,

    'author': "Kevin Kong",
    'website': "http://www.odoomommy.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'basic',
    'version': '14.7.5',

    # any module necessary for this one to work correctly
    'depends': ['mail'],

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
