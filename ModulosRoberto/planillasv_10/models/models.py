# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression
from odoo.exceptions import ValidationError
from datetime import datetime


#Modificaciones a la cuenta analitica para que se presente
#La forma en el la compra
class sv_employee(models.Model):
	_inherit = 'hr.employee'
	sv_nombre_dui= fields.Char("Nombres segun DUI/PASAPORTE")
	sv_apellido_dui=fields.Char("Apellidos segun DUI/PASAPORTE")
	sv_afp=fields.Char("AFP")
	prestamos_ids = fields.One2many('planillasv_10.prestamo', 'employee_id', 'Prestamos', help="Prestamos personales")
	bonos_ids = fields.One2many('planillasv_10.bono', 'employee_id', 'Bonos', help="Bonos")
	incapacidad_ids = fields.One2many('planillasv_10.incapacidad', 'employee_id', 'Incapacidad', help="Incapacidad")
	
	@api.multi
	def salaryprestamo(self,banco_code,fecha):
		total = 0.00
		for record in self:
			for prestamo in record.prestamos_ids:
				if (prestamo.banco_id.code==banco_code):
					if (fecha>=prestamo.sv_fecha_inicio):
						if (fecha<=prestamo.sv_fecha_fin):
							total = total + prestamo.sv_cuota
		return total
	
	@api.multi
	def salaryincapacidadpagocompleto(self,banco_code,fecha1,fecha2):
		total = 0.00
		for record in self:
			for prestamo in record.incapacidad_ids:
				if (prestamo.sv_fecha>=fecha1):
					if (prestamo.sv_fecha<=fecha2):
						total = total + prestamo.sv_dias_pago_completo
		return total
	
	@api.multi
	def salaryincapacidadpagoparcial(self,banco_code,fecha1,fecha2):
		total = 0.00
		for record in self:
			for prestamo in record.incapacidad_ids:
				if (prestamo.sv_fecha>=fecha1):
					if (prestamo.sv_fecha<=fecha2):
						total = total + prestamo.sv_dias_pago_parcial
		return total
	
	
	@api.multi
	def salarybono(self,fecha_start,fecha_end):
		total = 0.00
		for record in self:
			for bono in record.bonos_ids:
				if (bono.vi_fecha>=fecha_start):
					if (bono.vi_fecha<fecha_end):
						total = total + bono.vi_monto
		return total
	
	@api.multi
	def salarybonopagado(self,fecha_start,fecha_end):
		total = 0.00
		for record in self:
			for bono in record.bonos_ids:
				if (bono.vi_fecha>=fecha_start):
					if (bono.vi_fecha<fecha_end):
						if (bono.vi_pagado==True):
							total = total + bono.vi_monto
		return total


class sv_hr_banco_prestamo(models.Model):
	_name = 'planillasv_10.banco'
	_description = "Registro de bancos para prestamos"
	name = fields.Char("Banco/Financiera/Otros", required=True)
	code = fields.Char("Codigo")
	comment = fields.Text("Comentario")


class sv_hr_prestamo(models.Model):
	_name = 'planillasv_10.prestamo'
	_description = "Registro de prestamos bancarios"
	name = fields.Char("Referencia", required=True)
	comment = fields.Text("Comentario")
	employee_id=fields.Many2one('hr.employee',string='Empleado')
	banco_id=fields.Many2one('planillasv_10.banco',string='Banco')
	sv_monto=fields.Float("Monto del prestamo")
	sv_cuota=fields.Float("Cuota del prestamo")
	sv_fecha=fields.Date("Fecha del prestamo")
	sv_fecha_inicio=fields.Date("Fecha de inicio de los pagos")
	sv_fecha_fin=fields.Date("Fecha de finalizacion de los pagos")
	sv_day=fields.Integer("Dia de pago")
	sv_documento=fields.Binary("Orden de descuento")
	sv_cuotas=fields.Integer("Cuotas totales")
	sv_filename=fields.Char("Nombre del archivo")

class sv_hr_salary_rule(models.Model):
	_inherit = 'hr.salary.rule'
	sv_proyecto=fields.Char("Nombre del proyecto")
	
class sv_hr_payslip(models.Model):
	_inherit = 'hr.payslip'
	sv_isr = fields.Float("Monto del ISR")
	sv_apply_isr = fields.Boolean("Fijar Monto del ISR")
	sv_days = fields.Integer('Dias en la planilla',readonly=True,compute='_compute_days')
	sv_he_diurna=fields.Integer("Horas extra diurnas")
	sv_he_nocturna=fields.Integer("Horas extra nocturnas")
	
	@api.one
	@api.depends('date_from', 'date_to')
	def _compute_days(self):
		if self.date_from:
			if self.date_to:
				fmt = '%Y-%m-%d'
				fromdate=self.date_from
				todate=self.date_to
				d1=datetime.strptime(fromdate, fmt)
				d2=datetime.strptime(todate, fmt)
				self.sv_days = ((d2 - d1).days)+1
			else:
				self.sv_days=30
		else:
			self.sv_days=30

class sv_hr_bono(models.Model):
	_name = 'planillasv_10.bono'
	_description = "Registro de bonos"
	name = fields.Char("razon", required=True)
	comment = fields.Text("Comentario")
	employee_id=fields.Many2one('hr.employee',string='Empleado')
	sv_monto=fields.Float("Monto del prestamo")
	sv_fecha=fields.Date("Fecha del bono")
	sv_pagado = fields.Boolean("Pagado")
	
class sv_hr_incapacidad(models.Model):
	_name = 'planillasv_10.incapacidad'
	_description = "Registro de incapacidad"
	name = fields.Char("razon", required=True)
	comment = fields.Text("Comentario")
	employee_id=fields.Many2one('hr.employee',string='Empleado')
	sv_dias_pago_completo=fields.Integer("Dias de pago compelto")
	sv_dias_pago_parcial=fields.Integer("Dias de pago parcial")
	sv_fecha=fields.Date("Fecha para considerar en planilla")

