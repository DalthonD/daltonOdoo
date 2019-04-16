odoo.define('strategikcrm.openwindows', function (require) {
"use strict";

var form_widget = require('web.form_widgets');
var core = require('web.core');
var _t = core._t;
var QWeb = core.qweb;

form_widget.WidgetButton.include({
    on_click: function() {
         if(this.node.attrs.custom === "click_presupuesto"){
            var x=document.getElementById('identidad').children[0].innerHTML;
            var r=document.getElementById('reporte').children[0].innerHTML;
            window.open('http://report.expertha.com/jasperserver/flow.html?_flowId=viewReportFlow&standAlone=true&j_acegi_security_check?&j_username=strategik&j_password=strategik&userLocale=es_SV&_flowId=viewReportFlow&ParentFolderUri=/Strategik_reports/contabilidad/trasacciones&reportUnit=/Strategik_reports/contabilidad/trasacciones/'+r+'&decorate=no&output=pdf&facturaId='+x);
            return;
         }
         this._super();
    },
});
});
