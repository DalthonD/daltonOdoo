# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, tools

class sv_purchase_report(models.Model):
    _name = 'strategiksv.reportesv.purchase.report'
    _auto = False
    name = fields.Char("Reporte de Compras")
    description = field.Char("Reporte Compras")
    company_id=fileds.Many2one('res_company.id', string="Company", help="Company")
    fecha = fields.Date("Fecha de la Factura")
    factura = fields.Many2one('account_invoice.reference', string="Factura", help="Número de referencia de factura")
    proveedor = fields.Char("Nombre del proveedor")
    #proveedor = fields.Char('')
    nrc = fields.Many2one('res_partner.vat', string="NRC", help="NRC")
    importacion = fields.Boolean("Importación")
    gravado = fields.Float("Compras Gravadas")
    exento = fields.Float("Compras Exentas")
    iva = fields.Float("IVA")
    retenido = fields.Float("Anticipo a Cuenta de IVA Retenido")
    percibido = fields.Float("Anticipo a Cuenta de IVA Percibido")
    excluido = fields.Float("Compras a Sujetos Excluidos")
    retencion3 = fields.Float("Retención a Terceros")

    @api.model_cr
    def init(self):
        self.env.cr.execute("""CREATE OR REPLACE VIEW sv_purchase_report AS (select * from (
select ai.date_invoice as fecha
	,ai.reference as factura
	,rp.name as proveedor
	,rp.vat as NRC
	,case
		when rp.country_id=211 then False
		when rp.country_id is null then False
		else True end as Importacion
	,/*Calculando el gravado (todo lo que tiene un impuesto aplicado de iva)*/
     (select coalesce(sum(price_subtotal_signed),0.00)
      from account_invoice_line ail
      where invoice_id=ai.id
	      and exists(select ailt.tax_id
					from account_invoice_line_tax ailt
				        inner join account_tax atx on ailt.tax_id=atx.id
				        inner join account_tax_group atg on atx.tax_group_id=atg.id
			         where ailt.invoice_line_id=ail.id and atg.name='iva')
      ) as Gravado,
      /*Calculando el excento que no tiene iva*/
     (Select coalesce(sum(price_subtotal_signed),0.00)
      from account_invoice_line ail
      where invoice_id=ai.id
	      and not exists(select ailt.tax_id
						 from account_invoice_line_tax ailt
				             inner join account_tax atx on ailt.tax_id=atx.id
				             inner join account_tax_group atg on atx.tax_group_id=atg.id
			             where ailt.invoice_line_id=ail.id and atg.name='iva')
      ) as Exento
      ,/*Calculando el iva*/
      (Select coalesce(sum(ait.amount),0.00)
       from account_invoice_tax ait
 	       inner join account_tax atx on ait.tax_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where invoice_id=ai.id
	       and atg.name='iva'
       ) as Iva
	   ,/*Calculando el retenido*/
      (Select coalesce(sum(ait.amount),0.00)
       from account_invoice_tax ait
 	       inner join account_tax atx on ait.tax_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where invoice_id=ai.id
	       and atg.name='retencion'
       ) as Retenido
	    ,/*Calculando el percibido*/
      (Select coalesce(sum(ait.amount),0.00)
       from account_invoice_tax ait
 	       inner join account_tax atx on ait.tax_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where invoice_id=ai.id
	       and atg.name='percepcion'
       ) as Percibido
         ,/*Calculando el excluido*/
      (Select coalesce(sum(ait.amount),0.00)
       from account_invoice_tax ait
 	       inner join account_tax atx on ait.tax_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where invoice_id=ai.id
	       and atg.name='excluido'
       ) as Excluido
	   ,/*Calculando el retencion a terceros*/
      (Select coalesce(sum(ait.amount),0.00)
       from account_invoice_tax ait
 	       inner join account_tax atx on ait.tax_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where invoice_id=ai.id
	       and atg.name='retencion3'
       ) as retencion3
from account_invoice ai
	inner join res_partner rp on ai.partner_id=rp.id
where ai.type='in_invoice'
	and ((ai.sv_no_tax is null ) or (ai.sv_no_tax=false))
	and ai.state in ('open','paid')
	and ((ai.sv_importacion_number is null) or (trim(ai.sv_importacion_number)=''))

union all

select min(SI.fecha) as fecha
               ,SI.sv_importacion_number as factura
               ,'DGT' as proveedor
               ,'DGT' as NRC
               ,True as Importacion
               ,sum (SI.Gravado) as  Gravado
               ,sum (SI.Exento) as  Exento
               ,sum (SI.Iva) as  Iva
               ,sum (SI.Retenido) as  Retenido
               ,sum (SI.Percibido) as  Percibido
               ,sum (SI.Excluido) as  Excluido
               ,sum (SI.retencion3) as  retencion3
from (
select ai.date_invoice as fecha
	,ai.reference as factura
	,ai.sv_importacion_number
	,rp.name as proveedor
	,rp.vat as NRC
	,case
		when rp.country_id=211 then False
		when rp.country_id is null then False
		else True end as Importacion
	,/*Calculando el gravado (todo lo que tiene un impuesto aplicado de iva)*/
     (select coalesce(sum(price_subtotal_signed),0.00)
      from account_invoice_line ail
      where invoice_id=ai.id
	      and exists(select ailt.tax_id
					from account_invoice_line_tax ailt
				        inner join account_tax atx on ailt.tax_id=atx.id
				        inner join account_tax_group atg on atx.tax_group_id=atg.id
			         where ailt.invoice_line_id=ail.id and atg.name='iva')
      ) as Gravado,
      /*Calculando el excento que no tiene iva*/
     (Select coalesce(sum(price_subtotal_signed),0.00)
      from account_invoice_line ail
      where invoice_id=ai.id
	      and not exists(select ailt.tax_id
						 from account_invoice_line_tax ailt
				             inner join account_tax atx on ailt.tax_id=atx.id
				             inner join account_tax_group atg on atx.tax_group_id=atg.id
			             where ailt.invoice_line_id=ail.id and atg.name='iva')
      ) as Exento
      ,/*Calculando el iva*/
      (Select coalesce(sum(ait.amount),0.00)
       from account_invoice_tax ait
 	       inner join account_tax atx on ait.tax_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where invoice_id=ai.id
	       and atg.name='iva'
       ) as Iva
	   ,/*Calculando el retenido*/
      (Select coalesce(sum(ait.amount),0.00)
       from account_invoice_tax ait
 	       inner join account_tax atx on ait.tax_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where invoice_id=ai.id
	       and atg.name='retencion'
       ) as Retenido
	    ,/*Calculando el percibido*/
      (Select coalesce(sum(ait.amount),0.00)
       from account_invoice_tax ait
 	       inner join account_tax atx on ait.tax_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where invoice_id=ai.id
	       and atg.name='percepcion'
       ) as Percibido
         ,/*Calculando el excluido*/
      (Select coalesce(sum(ait.amount),0.00)
       from account_invoice_tax ait
 	       inner join account_tax atx on ait.tax_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where invoice_id=ai.id
	       and atg.name='excluido'
       ) as Excluido
	   ,/*Calculando el retencion a terceros*/
      (Select coalesce(sum(ait.amount),0.00)
       from account_invoice_tax ait
 	       inner join account_tax atx on ait.tax_id=atx.id
	       inner join account_tax_group atg on atx.tax_group_id=atg.id
       where invoice_id=ai.id
	       and atg.name='retencion3'
       ) as retencion3
from account_invoice ai
	inner join res_partner rp on ai.partner_id=rp.id
where ai.type='in_invoice'
	and ((ai.sv_no_tax is null ) or (ai.sv_no_tax=false))
	and ai.state in ('open','paid')
	and ((ai.sv_importacion_number is not null) or (trim(ai.sv_importacion_number)!=''))
) SI
group by   SI.sv_importacion_number

union all

select aml.date as fecha
               ,am.ref as factura
               ,rp.name as proveedor
               ,rp.vat as NRC
               ,False as Importacion
               ,0.0 as  Gravado
               ,0.0 as  Exento
               ,0.0  as  Iva
               ,0.0 as  Retenido
               ,aml.debit as  Percibido
               ,0.0  as  Excluido
               ,0.0 as  retencion3
 from account_move_line aml
 	inner join account_move am on aml.move_id=am.id
 	inner join account_tax at on aml.account_id=at.account_id
 	inner join account_tax_group atg on at.tax_group_id=atg.id
 	left join res_partner rp on aml.partner_id=rp.id
 where atg.name='percepcion' and not exists (select id from account_invoice ai where ai.move_id=am.id)
	and am.state='posted') S order by s.Fecha, s.Factura)""")


# class reportesv(models.Model):
#     _name = 'reportesv.reportesv'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
