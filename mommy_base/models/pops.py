#!/usr/bin/python3
# @Time    : 2022-09-05
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _

class message_pops_up(models.TransientModel):
    _name = "mommy.message.popsup"

    title = fields.Char("标题")
    content = fields.Char("消息内容",readonly=True)
    
    @api.model
    def get_action(self):
        form_view_id = self.env.ref('window_pops.customize_window_form_view').id
        return {
            'name':self.name,
            'type':'ir.actions.act_window',
            'res_model':'window.pops',
            'view_mode':'form',
            'target':'new',
            'res_id':self.id,
            'views':[(form_view_id,'form'),],
        }

    def btn_OK(self):
        return {
            'type':'ir.actions.act_window_close'
        }