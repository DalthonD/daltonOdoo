# -*- coding: utf-8 -*-
import time
from odoo import models, fields, api, tools

class strategiksv_purchase_report_pdf(models.Model):
    _name = 'report.reportesv.strategiksv_purchase_report_pdf'
    _auto = False

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report'].\
            _get_report_from_name('reportesv.strategiksv_purchase_report_pdf')
        if data and data.get('form')\
            and  data.get('form').get('company_id')\
            and  data.get('form').get('date_year')\
            and  data.get('form').get('date_month'):
            docids = self.env['res.company'].browse(data['form']['company_id'][0])
        return {'doc_ids': self.env['wizard.sv.purchase.report'].browse(data['ids']),
                'doc_model': report.model,
                'docs': self.env['res.company'].browse(data['form']['company_id'][0]),
                'data': data,
                }

    """def render_html(self):
        report_obj = self.pool['report']
        report = report_obj._get_report_from_name(uid, 'purchase_report.strategiksv_purchase_report_pdf')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': report.model,
            'docs': create_view(),
            'time': time,
        }
        return report_obj.render('purchase_report.strategiksv_purchase_report_pdf', docargs)


class sv_report_reportWizard(models.TransientModel):
    _name = "report_wizard"
    _description = "Wizard para reporte de consumidores"

    company_id=fields.Many2one('res.company', string="Company", help='Company',default=lambda self: self.env.user.company_id.id)
    date_month = fields.Selection([('1','Enero'),('2','Febrero'),('3','Marzo'),('4','Abril'),('5','Mayo'),('6','Junio'),('7','Julio'),('8','Agosto'),('9','Septiembre'),('10','Octubre'),('11','Noviembre'),('12','Diciembre')],string='Mes de facturación', default='1',required=True)
    date_year = fields.Integer("Año de facturación", default=2018, requiered=True)
    show_serie = fields.Boolean("Ventas a Consumidor", default=False)
    serie_lenght = fields.Integer("Agrupación de facturas", default = 1)"""

    """@api.multi
    def check_report(self):
        data = {}
        data['form'] = self.read(['company_id', 'date_month', 'date_year', 'serie_lenght'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['company_id','date_month','date_year'])[0])
        report = purchase_report_pdf(data['form'][0],data['form'][1],data['form'][2])
        return self.env['report'].get_action(self, 'purchase_report.strategiksv_purchase_report_pdf', data=data)"""
