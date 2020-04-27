from odoo import fields, api, models
from odoo.exceptions import UserError
from datetime import datetime
import pytz
from pytz import timezone
from odoo.exceptions import Warning

class MsQuery(models.Model):
    _name = "ms.query"
    _description = "Execute Query"
    _inherit = ['mail.thread']
    
    backup = fields.Text('Backup Syntax', help="Backup your query if needed")
    name = fields.Text('Syntax', required=True)
    result = fields.Text('Result')

    def get_real_datetime(self):
        if not self.env.user.tz :
            raise Warning("Please set your timezone in Users menu.")
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz))
    
    @api.multi
    def execute_query(self):
        if not self.name :
            return
        while self.name[:1] == ' ' :
            self.name = self.name[1:]
        prefix = self.name[:6].upper()
        try :
            self._cr.execute(self.name)
        except Exception as e :
            raise UserError(e)

        if prefix == 'SELECT' :
            result = self._cr.fetchall()
            if result :
               self.result = result[0]
            else :
                self.result = "Data not found"
        elif prefix == 'UPDATE' :
            self.result = '%d row affected'%(self._cr.rowcount)
        else :
            self.result = 'Successful'
        self.message_post('%s<br><br>Executed on %s'%(self.name,str(self.get_real_datetime())[:19]))
