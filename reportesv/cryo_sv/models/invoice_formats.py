class ReportInvoiceFac(models.AbstractModel):
    _name = 'report.cryo_sv.account_invoice_formato_cryo'
    _description = 'Formato de Facturas para Cryo'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('cryo_sv.account_invoice_formato_cryo')
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(docids),
            'report_type': data.get('report_type') if data else '',
        }

class ReportInvoiceCCF(models.AbstractModel):
    _name = 'report.cryo_sv.account_invoice_ccf_cryo'
    _description = 'Formato de CCF para Cryo'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('cryo_sv.account_invoice_ccf_cryo')
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(docids),
            'report_type': data.get('report_type') if data else '',
        }
