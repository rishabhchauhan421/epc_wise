/* Reason: Unified script to handle party filtering, bank fetching, and company-specific payment accounts. */
frappe.ui.form.on("Outgoing Payment Request", {
	setup: function (frm) {
		// Limit Party Type to these four standard types
		frm.set_query("party_type", function () {
			return {
				filters: { name: ["in", ["Supplier", "Employee", "Customer", "Member"]] },
			};
		});
	},

	refresh: function (frm) {
		// Filter: Only show Bank Accounts belonging to the specific Company on this record
		frm.set_query("paid_from_account", function () {
			return {
				filters: {
					company: frm.doc.company,
					is_company_account: 1,
				},
			};
		});

		// Trigger the mandatory check on load if already in a funding state
		toggle_bank_requirement(frm);
	},

	party_type: function (frm) {
		// Clear dependent fields if the Category changes to prevent data mismatch
		frm.set_value("party", "");
		frm.set_value("bank_account", "");
	},

	party: function (frm) {
		if (frm.doc.party) {
			// Only show bank accounts registered to this specific Supplier/Employee
			frm.set_query("bank_account", function () {
				return {
					filters: {
						party_type: frm.doc.party_type,
						party: frm.doc.party,
					},
				};
			});
		}
	},

	bank_account: function (frm) {
		if (frm.doc.bank_account) {
			frappe.db.get_value(
				"Bank Account",
				frm.doc.bank_account,
				["bank_account_no", "branch_code"],
				(r) => {
					frm.set_value("bank_account_no", r.bank_account_no);
					frm.set_value("branch_code", r.branch_code);
				},
			);
		}
	},

	workflow_state: function (frm) {
		toggle_bank_requirement(frm);
	},
});

// Helper function to handle field requirements based on state
var toggle_bank_requirement = function (frm) {
	const funding_states = ["Waiting for Funds", "Paid", "Pending Approval from Ma'am"];
	if (funding_states.includes(frm.doc.workflow_state)) {
		frm.set_df_property("paid_from_account", "reqd", 1);
	} else {
		frm.set_df_property("paid_from_account", "reqd", 0);
	}
};
