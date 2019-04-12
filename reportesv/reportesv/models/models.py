# -*- coding: utf-8 -*-
import time
from odoo import tools
from odoo import models, fields, api, tools
from dateutil.parser import parse
from odoo.exceptions import UserError

class sv_purchase_report(models.Model):
    _name = 'strategiksv.reportesv.purchase.report'
    _description = "Reporte de Compras"
    _auto = False

    name = fields.Char("Reporte de Compras")
    company_id=fields.Many2one('res_company.id', string="Company", help="Company")
    mes = fields.Integer("Mes", help="Mes de facturación")
    anio = fields.Integer("Año", help="Año de facturación")
    nrc = fields.Char("NRC")
    factura = fields.Char("Factura", help="Número de referencia de factura")
    fecha = fields.Date("Fecha")
    proveedor = fields.Char("Proveedor")
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
        self.env.cr.execute("""CREATE OR REPLACE VIEW strategiksv_reportesv_purchase_report AS (select * from (
select 10000000+ai.id as id
    ,ai.company_id as company_id
    ,date_part('year',COALESCE(ai.sv_fecha_tax,ai.date_invoice)) as anio
    ,date_part('month',COALESCE(ai.sv_fecha_tax,ai.date_invoice)) as mes
    ,ai.date_invoice as fecha
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

select 20000000+SI.id as id
			   ,SI.company_id as company_id
               ,SI.mes as mes
               ,SI.anio as anio
			   ,min(SI.fecha) as fecha
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
select ai.id as id
    ,ai.company_id as company_id
    ,date_part('year',COALESCE(ai.sv_fecha_tax,ai.date_invoice)) as anio
    ,date_part('month',COALESCE(ai.sv_fecha_tax,ai.date_invoice)) as mes
	,ai.date_invoice as fecha
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
group by   SI.sv_importacion_number, SI.id, SI.anio, SI.mes, SI.company_id

union all

select 30000000+aml.id as id
               ,am.company_id as company_id
               ,date_part('year', am.date) as anio
               ,date_part('month', am.date) as mes
			   ,aml.date as fecha
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

class sv_taxpayer_sales_report(models.Model):
    _name = 'strategiksv.reportesv.sales_taxpayer.report'
    _description = "Reporte de Ventas a Contribuyentes"
    _auto = False

    name = fields.Char("Reporte de Ventas a Contribuyentes")
    company_id=fields.Many2one('res_company.id', string="Company", help="Company")
    anio = fields.Integer("Año")
    mes = fields.Integer("Mes")
    fecha = fields.Date("Fecha de Factura")
    factura = fields.Char("Factura", help="Número de referencia de factura")
    cliente = fields.Char("Cliente")
    nrc = fields.Char("NRC")
    estado = fields.Char("Estado")
    gravado = fields.Float("Gravado")
    exento = fields.Float("Exento")
    iva = fields.Float("IVA")
    retenido = fields.Float("Retenido")
    percibido = fields.Float("Percibido")

    @api.model_cr
    def init(self):
        self.env.cr.execute("""CREATE OR REPLACE VIEW strategiksv_reportesv_sales_taxpayer_report AS (select * from(
select 10000000+ai.id as id
	,ai.company_id as company_id
	,date_part('year',COALESCE(ai.sv_fecha_tax,ai.date_invoice)) as anio
	,date_part('month',COALESCE(ai.sv_fecha_tax,ai.date_invoice)) as mes
	,ai.date_invoice as fecha
	,ai.reference as factura
	,rp.name as cliente
	,rp.vat as NRC
	,ai.state as estado
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
       )*(case when ai.type='out_refund' then -1 else 1 end) as Iva
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
from account_invoice ai
	inner join res_partner rp on ai.partner_id=rp.id
	left join account_fiscal_position afp on ai.fiscal_position_id=afp.id
where ((ai.type='out_invoice') or (ai.type='out_refund'))
	and ((ai.sv_no_tax is null ) or (ai.sv_no_tax=false))
	and afp.sv_contribuyente=True
	and ai.state in ('open','paid')

union

select 20000000+ai.id as id
	,ai.company_id as company_id
	,date_part('year',COALESCE(ai.sv_fecha_tax,ai.date_invoice)) as anio
	,date_part('month',COALESCE(ai.sv_fecha_tax,ai.date_invoice)) as mes
	,ai.date_invoice as fecha
	,ai.reference as factura
	,'Anulado' as cliente
	,rp.vat as NRC
	,ai.state as estado
	,0.0 as Gravado
	,0.0 as Exento
    ,0.0 as Iva
	,0.0 as Retenido
	,0.0 as Percibido
from account_invoice ai
	inner join res_partner rp on ai.partner_id=rp.id
	left join account_fiscal_position afp on ai.fiscal_position_id=afp.id
where ai.type='out_invoice'
	and ((ai.sv_no_tax is null ) or (ai.sv_no_tax=false))
	and afp.sv_contribuyente=True
	and ai.state in ('cancel')
)S order by s.fecha, s.factura)""")

class sv_consumer_sales_report(models.Model):
    _name = 'strategiksv.reportesv.sales_consumer.report'
    _description = "Reporte de Ventas a Consumidores"
    _auto = False

    name = fields.Char("Reporte de Ventas a Consumidores")
    company_id=fields.Many2one('res_company.id', string="Company", help="Company")
    fecha = fields.Date("Fecha de Factura")
    grupo = fields.Integer("Grupo")
    delnum = fields.Char("Desde")
    alnum = fields.Char("Hasta")
    exento = fields.Float("Exento")
    gravadolocal = fields.Float("Gravado Local")
    gravadoexportacion = fields.Float("Gravado Exportación")
    ivalocal = fields.Float("IVA Local")
    ivaexportacion = fields.Float("IVA Exportación")
    retenido = fields.Float("Retenido")
    estado = fields.Char("Estado")

    @api.model_cr
    def init(self):
        self.env.cr.execute("""CREATE OR REPLACE VIEW strategiksv_reportesv_sales_consumer_report AS (Select
    10000000+SS.id as id
    ,SS.Fecha
	,SS.grupo
	,min(SS.Factura) as DELNum
	,max(SS.Factura) as ALNum
	,sum(SS.exento) as Exento
	,sum(SS.GravadoLocal) as GravadoLocal
	,sum(SS.GravadoExportacion) as GravadoExportacion
	,Sum(SS.ivaLocal) as IvaLocal
	,Sum(SS.ivaexportacion) as IvaExportacion
	,Sum(SS.retenido) as Retenido
	,estado
FROM (
select 20000000+S.id as id
    ,S.fecha
	,S.factura
	,S.estado
	,S.grupo
	,S.exento
	,case
		when S.sv_region='Local' then S.Gravado
		else 0.00 end as GravadoLocal
	,case
		when S.sv_region!='Local' then S.Gravado
		else 0.00 end as GravadoExportacion
	,case
		when S.sv_region='Local' then S.Iva
		else 0.00 end as IvaLocal
	,case
		when S.sv_region!='Local' then S.Iva
		else 0.00 end as IvaExportacion
	,S.Retenido
from(
select 30000000+ai.id as id, ai.date_invoice as fecha
	,coalesce(ai.reference,ai.number) as factura
	,'valid' as estado
	,FG.grupo
	,afp.sv_region
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
from account_invoice ai
	inner join res_partner rp on ai.partner_id=rp.id
	inner join (select * from FacturasAgrupadas( 1, 1 , 2018 , 5 )) FG on ai.id=FG.invoice_id
	left join account_fiscal_position afp on ai.fiscal_position_id=afp.id
where ai.type='out_invoice'
	and ((ai.sv_no_tax is null ) or (ai.sv_no_tax=false))
	and afp.sv_contribuyente=False
	and ai.state in ('open','paid')

union

select 40000000+ai.id as id, ai.date_invoice as fecha
	,coalesce(ai.reference,ai.number) as factura
	,ai.state as estado
	,FG.grupo
	,afp.sv_region
	,0.0 as Gravado
	,0.0 as Exento
    ,0.0 as Iva
	,0.0 as Retenido
from account_invoice ai
	inner join res_partner rp on ai.partner_id=rp.id
	inner join (select * from FacturasAgrupadas( 1 , 1, 2018 , 5)) FG on ai.id=FG.invoice_id
	left join account_fiscal_position afp on ai.fiscal_position_id=afp.id
where ai.type='out_invoice'
	and ((ai.sv_no_tax is null ) or (ai.sv_no_tax=false))
	and afp.sv_contribuyente=False
	and ai.state in ('cancel')
)S )SS group by SS.fecha, SS.Grupo,SS.estado, SS.id order by SS.fecha, SS.Grupo)""")

class sv_consumer_sales_reportWizard(models.TransientModel):
    _name = "strategiksv_reportesv_sales_consumer_report.wizard"
    _description = "Wizard para reporte de consumidores"

    company_id=fields.Many2one('res.company',string="Company",help='Company',default=lambda self: self.env.user.company_id.id)
    date_month = fields.Selection([('1','Enero'),('2','Febrero'),('3','Marzo'),('4','Abril'),('5','Mayo'),('6','Junio'),('7','Julio'),('8','Agosto'),('9','Septiembre'),('10','Octubre'),('11','Noviembre'),('12','Diciembre')],string='Mes de facturación',required=True)
    date_year = fields.Integer("Año", string ="Año de facturación", requiered=True)

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['company_id', 'date_month', 'date_year'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['company_id','date_month','date_year'])[0])
        return self.env['report'].get_action(self, 'strategiksv.reportesv.sales_consumer.report', data=data)
