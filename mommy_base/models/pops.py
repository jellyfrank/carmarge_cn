#!/usr/bin/python3
# @Time    : 2022-09-05
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _

class message_pops_up(models.TransientModel):
    _name = "mommy.message.popsup"

    name = fields.Char("Title")
    content = fields.Char("Message Content",readonly=True, default="This is a default message, using _action_pops_up_confirm of context model method to replace.")
    
    @api.model
    def get_action(self):
        form_view_id = self.env.ref('mommy_base.customize_window_form_view').id
        return {
            'name':self.name,
            'type':'ir.actions.act_window',
            'res_model':'mommy.message.popsup',
            'view_mode':'form',
            'target':'new',
            'res_id':self.id,
            'views':[(form_view_id,'form'),],
            'context':self._context
        }

    @api.model
    def get_confirm_action(self):
        form_view_id = self.env.ref('mommy_base.view_pops_up_confirm_form').id
        return {
            'name':self.name,
            'type':'ir.actions.act_window',
            'res_model':'mommy.message.popsup',
            'view_mode':'form',
            'target':'new',
            'res_id':self.id,
            'views':[(form_view_id,'form'),],
            'context':self._context
        }

    def btn_OK(self):
        return {
            'type':'ir.actions.act_window_close'
        }

    def button_confirm(self):
        if hasattr(self.active_records,'_action_pops_up_confirm'):
            self.active_records._action_pops_up_confirm()
    