# -*- coding: utf-8 -*-
import time
from odoo import tools
from odoo import models, fields, api
from collections import defaultdict
from dateutil.parser import parse
from odoo.exceptions import UserError

class sv_purchase_report(models.AbstractModel):
    _name = 'purchase_report'
    _description = "Reporte de Compras"
    _auto = False

class sv_reportWizard(models.TransientModel):
    _name = 'report_wizard'
    _inherit = 'ir.actions.report'
    _description = 'qweb-pdf'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)
    date_month = fields.Selection([(1,'Enero'),(2,'Febrero'),(3,'Marzo'),(4,'Abril'),(5,'Mayo'),(6,'Junio'),(7,'Julio'),(8,'Agosto'),(9,'Septiembre'),(10,'Octubre'),(11,'Noviembre'),(12,'Diciembre')],string='Mes de facturación', default=1,required=True)
    date_year = fields.Integer("Año de facturación", default=2018 ,requiered=True)
    serie_lenght = fields.Integer("Agrupación de facturas", default = 1)

    @api.model_cr
    def create_view(self):
        if self._sql:
            if self.env.cr.execute(self._sql):
                reg = list(self.env.cr.fetchall())
                if reg:
                    return reg
                else:
                    raise TypeError("No returning. Empty")
            else:
                raise TypeError("Not executed")
        else:
            raise NameError("SQL no listo s%", self._sql)

    @api.multi
    def get_header_info(self):
        compania_info = self.env['res_company']
        id_needed = compania_info.search([('company_id', '=', self._companyId)], limit=1).id
        compania = compania_info.browse(id_needed)
        header = {
            'name' : compania.name,
            'nit': compania.sv_nit,
            'nrc': compania.sv_nrc,
            'contador': compania.sv_revisa_partida,
        }
        return header

    @api.model
    def get_html_report(self, id, report_name):
        report = self._get_report_from_name(report_name)
        document = report.render_qweb_html([id], data={})
        if document:
            return document
        return False

    @api.model
    def render_html(self):
        report_obj = self.pool['report']
        report = report_obj._get_report_from_name(uid, 'purchase_report.strategiksv_purchase_report_pdf')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': report.model,
            'docs': create_view(),
            'time': time,
        }
        return report_obj.render('purchase_report.strategiksv_purchase_report_pdf', docargs)

    #Metodo invocado para reporte de compras
    @api.multi
    def check_purchase_report(self):
        data = {}
        data['form'] = self.read(['company_id','date_year','date_month'])[0:]
        if len(data['form'])>0:
            self._sql = """CREATE OR REPLACE VIEW strategiksv_reportesv_purchase_report AS (select * from (select ai.date_invoice as fecha
            ,ai.reference as factura
            ,ai.reference as name
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
            where ailt.invoice_line_id=ail.id and atg.name='iva')) as Exento
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
            where ai.company_id= {0}
            and date_part('year',COALESCE(ai.sv_fecha_tax,ai.date_invoice))=  {1}
            and date_part('month',COALESCE(ai.sv_fecha_tax,ai.date_invoice))=  {2}
            and ai.type='in_invoice'
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
            from (select ai.date_invoice as fecha
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
            where ai.company_id= {0}
            and date_part('year',COALESCE(ai.sv_fecha_tax,ai.date_invoice))= {1}
            and date_part('month',COALESCE(ai.sv_fecha_tax,ai.date_invoice))= {2}
            and ai.type='in_invoice'
            and ((ai.sv_no_tax is null ) or (ai.sv_no_tax=false))
            and ai.state in ('open','paid')
            and ((ai.sv_importacion_number is not null) or (trim(ai.sv_importacion_number)!=''))
            ) SI group by   SI.sv_importacion_number

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
            where atg.name='percepcion' and not exists (select id from account_invoice ai where ai.move_id=am.id and ai.company_id= {0} )
            and date_part('year',am.date)= {1}
            and date_part('month',am.date)= {2}
            and am.company_id= {0}
            and am.state='posted') S order by s.Fecha, s.Factura)""".format(data['form'][0]['company_id'][0],data['form'][0]['date_year'],data['form'][0]['date_month'])
            self._companyId = data['form'][0]['company_id'][0]
        else:
            raise NameError(data['form'],data['form'][0]['company_id'][0],data['form'][0]['date_year'],data['form'][0]['date_month'])
        data = {
            'ids': self._ids,
            'model': 'report_wizard',
            'docs': create_view()
        }
        return self.env.ref('purchase_report.purchase_report_pdf').report_action(self, data)

    #Metodo para invocar reporte de ventas a Contribuyentes
    @api.multi
    def check_taxpayer_report(self):
        data = {}
        data['form'] = self.read(['company_id','date_year','date_month'])[0:]
        if len(data['form'])>0:
            self._sql = """CREATE OR REPLACE VIEW strategiksv_reportesv_taxpayer_report AS (select * from(
            select ai.date_invoice as fecha
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
            where ai.company_id= {0}
            and date_part('year',COALESCE(ai.sv_fecha_tax,ai.date_invoice))= {1}
            and date_part('month',COALESCE(ai.sv_fecha_tax,ai.date_invoice))= {2}
            and ((ai.type='out_invoice') or (ai.type='out_refund'))
            and ((ai.sv_no_tax is null ) or (ai.sv_no_tax=false))
            and afp.sv_contribuyente=True
            and ai.state in ('open','paid')

            union

            select ai.date_invoice as fecha
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
            where ai.company_id=  {0}
            and date_part('year',COALESCE(ai.sv_fecha_tax,ai.date_invoice))=  {1}
            and date_part('month',COALESCE(ai.sv_fecha_tax,ai.date_invoice))= {2}
            and ai.type='out_invoice'
            and ((ai.sv_no_tax is null ) or (ai.sv_no_tax=false))
            and afp.sv_contribuyente=True
            and ai.state in ('cancel')
            )S order by s.fecha, s.factura))""".format(data['form'][0]['company_id'][0],data['form'][0]['date_year'],data['form'][0]['date_month'])
            self._companyId = data['form'][0]['company_id'][0]
        else:
            raise NameError(data['form'],data['form'][0]['company_id'][0],data['form'][0]['date_year'],data['form'][0]['date_month'])
        datas = {
            'ids': self._ids,
            'model': 'report_wizard',
            'docs': create_view()
        }
        return self.env.ref('taxpayer_report.taxpayer_report_pdf').report_action(self, data=datas)

    #Metodo para invocar reporte de ventas a Consumidores
    @api.multi
    def check_consumer_report(self):
        data = {}
        data['form'] = self.read(['company_id','date_year','date_month','serie_lenght'])[0:]
        if len(data['form'])>0:
            self._sql = """CREATE OR REPLACE FUNCTION public.facturasagrupadas(p_company_id integer, month_number integer, year_number integer, p_series_lenght integer)
            RETURNS TABLE(invoice_id integer, factura_number character varying, factura_status character varying, grupo integer)
            LANGUAGE plpgsql
            AS $function$

            DECLARE
            var_r record;
            var_serie varchar;
            var_fecha date;
            var_correlativo int;
            var_estado varchar;
            var_grupo int;
            BEGIN
            var_grupo :=0;
            FOR var_r IN (select ROW_NUMBER () OVER (ORDER BY f.date_invoice,coalesce(F.reference,F.number))  as Registro
            ,left(coalesce(F.reference,F.number),p_series_lenght) as Serie
            ,cast(right(coalesce(F.reference,F.number),(length(coalesce(F.reference,F.number))-p_series_lenght)) as Integer) as correlativo
            ,F.date_invoice as fecha
            ,case
            when F.state='cancel' then 'ANULADA'
            else 'Valida' end as estado
            ,coalesce(F.reference,F.number) as factura,F.id
            from Account_invoice F
            inner join account_fiscal_position afp on F.fiscal_position_id=afp.id
            where date_part('year',COALESCE(F.sv_fecha_tax,F.date_invoice))= year_number
            and date_part('month',COALESCE(F.sv_fecha_tax,F.date_invoice))= month_number
            and F.state<>'draft' and F.company_id=p_company_id
            and F.type in ('out_invoice')
            and ((F.sv_no_tax is null ) or (F.sv_no_tax=false))
            and afp.sv_contribuyente=False
            order by fecha,factura )
            LOOP
            invoice_id := var_r.id;
            factura_number := var_r.Factura;
            factura_status := var_r.estado;
            if ((var_r.Serie=var_serie) and (var_r.fecha=var_Fecha) and (var_r.estado=var_estado) and (var_r.correlativo=(var_correlativo+1))) then
            grupo := var_grupo;
            else
            var_grupo := var_grupo+1;
            grupo := var_grupo;
            end if;
            var_serie := var_r.Serie;
            var_fecha := var_r.fecha;
            var_estado := var_r.estado;
            var_correlativo := var_r.correlativo;

            RETURN NEXT;
            END LOOP;
            END;
            $function$;

            CREATE OR REPLACE VIEW strategiksv_reportesv_consumer_report AS (Select
            SS.Fecha
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
            select S.fecha
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
            select ai.date_invoice as fecha
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
            inner join (select * from FacturasAgrupadas({0} , {2}, {1} , {3})) FG on ai.id=FG.invoice_id
            left join account_fiscal_position afp on ai.fiscal_position_id=afp.id
            where ai.company_id= {0}
            and date_part('year',COALESCE(ai.sv_fecha_tax,ai.date_invoice))= {1}
            and date_part('month',COALESCE(ai.sv_fecha_tax,ai.date_invoice))=  {2}
            and ai.type='out_invoice'
            and ((ai.sv_no_tax is null ) or (ai.sv_no_tax=false))
            and afp.sv_contribuyente=False
            and ai.state in ('open','paid')

            union

            select ai.date_invoice as fecha
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
            inner join (select * from FacturasAgrupadas( {0} , {2}, {1} , {3})) FG on ai.id=FG.invoice_id
            left join account_fiscal_position afp on ai.fiscal_position_id=afp.id
            where ai.company_id= {0}
            and date_part('year',COALESCE(ai.sv_fecha_tax,ai.date_invoice))= {1}
            and date_part('month',COALESCE(ai.sv_fecha_tax,ai.date_invoice))= {2}
            and ai.type='out_invoice'
            and ((ai.sv_no_tax is null ) or (ai.sv_no_tax=false))
            and afp.sv_contribuyente=False
            and ai.state in ('cancel')
            )S )SS group by SS.fecha, SS.Grupo,SS.estado order by SS.fecha, SS.Grupo);""".format(data['form'][0]['company_id'][0],data['form'][0]['date_year'],data['form'][0]['date_month'],data['form'][0]['serie_lenght'])
            self._companyId = data['form'][0]['company_id'][0]
        else:
            raise NameError(data['form'],data['form'][0]['company_id'][0],data['form'][0]['date_year'],data['form'][0]['date_month'])
        datas = {
            'ids': self._ids,
            'model': 'report_wizard',
            'docs': create_view()
        }
        return self.env.ref('consumer_report.consumer_report_pdf').report_action(self, data=datas)
