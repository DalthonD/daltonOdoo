odoo.define('cryo_sv.ReceiptScreenWidget', function (require) {
    'use strict';
    var screens = require('point_of_sale.screens');
    var ReceiptScreenWidget = screens.ReceiptScreenWidget;
    var core = require('web.core');    
    var QWeb = core.qweb;

	ReceiptScreenWidget.include({
	
		get_iswallet: function () {
			var order = this.pos.get_order();
			var result=false;
			var x = order.orderlines.length;
			for (var i=0;i<x;i++){
				var line = order.orderlines.models[i];
				if (line.product.display_name.includes("Wallet")){
					result=true;
				}
			}
			return result;
		 },
	});
});;
