# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class MailThread(models.AbstractModel):
    _inherit = "mail.thread"    

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        """ Si en el contexto se envia add_chatter_autofollow=False
            no se agregaran como followers. """     
        add_chatter_autofollow = self.env.context.get('add_chatter_autofollow', True)
        # Si venimos de pop-up mail compose view from sale.order, 
        # no suscribir
        if self.env.context.get('params', False) and self.env.context.get('params').get('model') == 'sale.order':
            add_chatter_autofollow = False
            
        if add_chatter_autofollow:
            return super(MailThread, self).message_subscribe(partner_ids=partner_ids, channel_ids=channel_ids, subtype_ids=subtype_ids)