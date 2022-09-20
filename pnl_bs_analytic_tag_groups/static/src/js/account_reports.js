odoo.define('pnl_bs_analytic_tag_groups.account_report', function (require) {
'use strict';

	var core = require('web.core');
	var Context = require('web.Context');
	var AccountReport = require('account_reports.account_report');
	
	AccountReport.include({
		
		events : _.extend({},AccountReport.prototype.events,{
			'click .account_analytic_tag_group' : 'groupby_analytic_tag',
		}),
		
		render: function() {
			this._super.apply(this,arguments);
			if(this._title != "account.financial.html.report") {
				this.$searchview_buttons.find('.o_account_reports_group_analytic_tag').remove();
			}
		},
		
		groupby_analytic_tag : function(event){
			if(this.report_options.analytic_tag) {
				this.report_options.analytic_tag = false
			}
			else {
				this.report_options.analytic_tag = true
			}
			this.reload();
		},
	
	})

});
