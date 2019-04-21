# -*- coding: utf-8 -*-
import time
from odoo import tools
from odoo import models, fields, api
from collections import defaultdict
from dateutil.parser import parse
from odoo.exceptions import UserError

"""class report_parser(object):
    def __init__(self, cr, uid, name, context):
        self.localcontext = {
            'next_seq': 'value',
            'select_value': self._function,
        }

    def set_context(self, objects, data, ids, report_type = None):
        self.localcontext['data'] = data
        self.localcontext['objects'] = objects"""

class sv_purchase_report(models.AbstractModel):
    _name = 'purchase_report'
    #_inherit = 'report.abstract_report'
    _template = 'strategiksv_purchase_report_pdf'
    #_wrapped_report_class = report_parser
    _description = "Reporte de Compras"
    _auto = False

    @api.model_cr
    def create_view(self, sql):
        self.env.cr.execute(sql)
        reg = list(self.env.cr.fetchall())
        return reg

class sv_reportWizard(models.TransientModel):
    _name = 'report_wizard'
    _description = "Wizard para reportes"

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id.id)
    date_month = fields.Selection([(1,'Enero'),(2,'Febrero'),(3,'Marzo'),(4,'Abril'),(5,'Mayo'),(6,'Junio'),(7,'Julio'),(8,'Agosto'),(9,'Septiembre'),(10,'Octubre'),(11,'Noviembre'),(12,'Diciembre')],string='Mes de facturación', default=1,required=True)
    date_year = fields.Integer("Año de facturación", default=2018 ,requiered=True)
    show_serie = fields.Boolean("Ventas a Consumidor")
    serie_lenght = fields.Integer("Agrupación de facturas", default = 1)

    @api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['company_id','date_year','date_month'])[0:]
        if len(data['form'])>0:
            self._sql = """CREATE OR REPLACE VIEW strategiksv_reportesv_purchase_report AS (select * from (select ai.date_invoice as fecha
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
        return self.env.ref('purchase_report.strategiksv_purchase_report_pdf').report_action(self, data=create_view()) #purchase_report.strategiksv_purchase_report_pdf  purchase_report.purchase_report_pdf

    @api.model_cr
    def create_view(self):
        self.env.cr.execute(self._sql)
        reg = list(self.env.cr.fetchall())
        return reg

    @api.multi
    def get_header_info(self):
        compania_info = self.env['res_company']
        id_needed = compania_info.search([('company_id', '=', self._companyId)], limit=1).id
        compania = compania_info.browse(id_needed)
        header = { 'name' : compania.name,
            'nit': compania.sv_nit,
            'nrc': compania.sv_nrc,
            'contador': compania.sv_revisa_partida,
        }
        return header

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
