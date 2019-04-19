# -*- coding: utf-8 -*-
##############################################################################


from odoo import api, fields, api, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID


class cryo_sv_pos(models.Model):
    inherit = 'pos.config'
    header_ticket=fields.Char("Header Ticket")
    footer_ticket=fields.Char("Footer Ticket")
    header_recibo=fields.Char("Header Recibo")
    footer_recibo=fields.Char("Footer Recibo")
    
