import logging
from odoo import fields, models, api, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import tools
import pytz
from pytz import timezone
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo import exceptions
_logger = logging.getLogger(__name__)

class res_company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    @api.multi
    def get_purchase_details(self, company_id, date_year, date_month):
        data = {}
        #data = []
        sql = """CREATE OR REPLACE VIEW strategiksv_reportesv_purchase_report AS (select * from (select ai.date_invoice as fecha
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
        and am.state='posted') S order by s.Fecha, s.Factura)""".format(company_id,date_year,date_month)
        tools.drop_view_if_exists(self._cr, 'strategiksv_reportesv_purchase_report')
        self._cr.execute(sql)
        #if self._cr.description: #Verify whether or not the query generated any tuple before fetching in order to avoid PogrammingError: No results when fetching
            #data = self._cr.dictfetchall()
            #data = list(self.env.cr.fetchall())
        data = self._cr.dictfetchall()
        return data

    @api.multi
    def get_taxpayer_details(self, company_id, date_year, date_month):
        #data = {}
        data = []
        sql = """CREATE OR REPLACE VIEW strategiksv_reportesv_taxpayer_report AS (select * from(
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
        )S order by s.fecha, s.factura)""".format(company_id,date_year,date_month)
        tools.drop_view_if_exists(self._cr, 'strategiksv_reportesv_taxpayer_report')
        self._cr.execute(sql)
        if self._cr.description: #Verify whether or not the query generated any tuple before fetching in order to avoid PogrammingError: No results when fetching
            #data = self._cr.dictfetchall()
            data = list(self._cr.fetchall())
        return data

    @api.multi
    def get_month_str(self, month):
        m = "No especificado"
        if self and month>0:
            months = {1: "Enero", 2: "Febrero",
                    3: "Marzo", 4: "Abril",
                    5: "Mayo", 6: "Junio",
                    7: "Julio", 8: "Agosto",
                    9: "Septiembre", 10: "Octubre",
                    11: "Noviembre", 12: "Diciembre"}
            m = months[month]
            return m
        else:
            return m
