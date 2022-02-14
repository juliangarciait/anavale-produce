odoo.define('pnl_bs_analytic_groups.account_report', function (require) {
'use strict';

	var core = require('web.core');
	var Context = require('web.Context');
	var AccountReport = require('account_reports.account_report');
	
	AccountReport.include({
		
		events : _.extend({},AccountReport.prototype.events,{
			'click .account_analytic_group' : 'groupby_analytic',
		}),
		
		render: function() {
			this._super.apply(this,arguments);
			if(this._title != "account.financial.html.report") {
				this.$searchview_buttons.find('.o_account_reports_group_analytic').remove();
			}
		},
		
		groupby_analytic : function(event){
			console.log("ACCOOOCCCCC-----------------",this)
			if(this.report_options.analytic_group) {
				console.log("ACCOOOCCCCC---------IFFFFFFF--------",this)
				this.report_options.analytic_group = false
			}
			else {
				console.log("ACCOOOCCCCC-------ELSEEEE----------",this)
				this.report_options.analytic_group = true
			}
			this.reload();
		},
	
	})

});
