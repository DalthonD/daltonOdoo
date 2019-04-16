# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT


class crm_quotation_format(models.Model):
	_name= 'strategikcrm.quotation_format'
	name= fields.Char("Nombre del formato")
	pre_content=fields.Text("Contenido previo")
	post_content=fields.Text("Contenido posterior")
	show_detail=fields.Boolean("Presentar lineas de detalle")
	company_id=fields.Many2one('res.company',string='Company',help='Company')
	

class crm_sale_order(models.Model):
	_inherit = 'sale.order'
	quotation_format_id=fields.Many2one('strategikcrm.quotation_format',string='Formato de cotizacion',help='Formato de cotización a utilizar')
	pre_content= fields.Text("Contenido previo",compute='_get_pre',store=True,required=False)
	post_content= fields.Text("Contenido posterior",compute='_get_pre',store=True,required=False)
	show_detail= fields.Boolean("Contenido posterior",compute='_get_pre',store=True,required=False)
	inside_content=fields.Text("Contenido interior")
	
	
	@api.one
	@api.depends('quotation_format_id')
	def _get_pre(self):
		if self.quotation_format_id != None:
			self.pre_content=self.quotation_format_id.pre_content
			self.post_content=self.quotation_format_id.post_content
			self.show_detail=self.quotation_format_id.show_detail

