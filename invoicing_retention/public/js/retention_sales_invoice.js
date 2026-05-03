// Script Name: Sales Invoice Retention Calculation
// Doctype: Sales Invoice

frappe.ui.form.on("Sales Invoice", {
	refresh: function (frm) {
		// calculation when net_total changes
		frm.trigger("calculate_retention");
		frm.set_query("account_head", "retention", function () {
			return {
				filters: {
					account_type: "Receivable",
					is_group: 0,
					company: frm.doc.company,
				},
			};
		});
	},

	net_total: function (frm) {
		frm.trigger("calculate_retention");
	},

	calculate_retention: function (frm) {
		if (!frm.doc.retention || !frm.doc.retention.length) return;

		let cumulative_total = 0;
		let net_total = flt(frm.doc.net_total);

		$.each(frm.doc.retention, function (i, d) {
			if (d.retention_rate) {
				d.retention_amount = flt((net_total * flt(d.retention_rate)) / 100);
				cumulative_total += flt(d.retention_amount);
				d.total = cumulative_total;
			} else {
				d.retention_amount = 0;
				d.total = cumulative_total;
			}
		});

		frm.refresh_field("retention");
		// frm.trigger("update_grand_total");
	},

	update_grand_total: function (frm) {
		//  Add retention total to grand total or keep separate
		// let total_retention = 0;
		// $.each(frm.doc.retention, function(i, d) {
		//     total_retention += flt(d.retention_amount);
		// });
		// frm.doc.total_retention = total_retention;
		// frm.refresh_field('total_retention');
	},
});

frappe.ui.form.on("Sales Invoice Retention", {
	retention_rate: function (frm, cdt, cdn) {
		frm.trigger("calculate_retention");
	},

	retention_amount: function (frm, cdt, cdn) {
		// Recalculate totals if retention_amount is manually changed
		let cumulative_total = 0;
		$.each(frm.doc.retention, function (i, d) {
			cumulative_total += flt(d.retention_amount);
			d.total = cumulative_total;
		});
		frm.refresh_field("retention");
	},

	retention_remove: function (frm, cdt, cdn) {
		frm.trigger("calculate_retention");
	},
	retention_add: function (frm, cdt, cdn) {
		frm.trigger("calculate_retention");
		
	},
});
