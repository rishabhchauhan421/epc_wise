// Copyright (c) 2026, EPC Wise

frappe.ui.form.on("Subcontractor Timesheet", {
	setup: function (frm) {
		frm.set_query("subcontractor", function () {
			return { filters: { supplier_group: "Sub Contractor" } };
		});
	},

	// 1. HARD VALIDATION ON SAVE
	validate: function (frm) {
		if (frm.doc.in_time && frm.doc.out_time) {
			// Using moment to parse time strings reliably
			let start = moment(frm.doc.in_time, "HH:mm:ss");
			let end = moment(frm.doc.out_time, "HH:mm:ss");

			if (!end.isAfter(start)) {
				frappe.validated = false;
				frappe.throw({
					title: __("Invalid Time"),
					message: __(
						"Out Time must be later than In Time. <br> Entered: " +
							frm.doc.in_time +
							" to " +
							frm.doc.out_time,
					),
				});
			}
		}
	},

	in_time: function (frm) {
		frm.trigger("calculate_hours");
	},

	out_time: function (frm) {
		frm.trigger("calculate_hours");
	},

	calculate_hours: function (frm) {
		if (frm.doc.in_time && frm.doc.out_time) {
			let start = moment(frm.doc.in_time, "HH:mm:ss");
			let end = moment(frm.doc.out_time, "HH:mm:ss");

			if (end.isAfter(start)) {
				// Get duration in decimal hours
				let duration = moment.duration(end.diff(start));
				let total = flt(duration.asHours(), 2);

				frm.set_value("total_hours", total);

				// OT Calculation (Standard shift is 9 hours)
				let ot = total > 9 ? flt(total - 9, 2) : 0;
				frm.set_value("ot_hours", ot);
			} else {
				frm.set_value("total_hours", 0);
				frm.set_value("ot_hours", 0);
			}

			frm.refresh_field("total_hours");
			frm.refresh_field("ot_hours");
		}
	},
});
