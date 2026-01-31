// Copyright (c) 2026, Rishabh Chauhan and contributors
// For license information, please see license.txt

frappe.query_reports["Subcontractor Salary Per Month"] = {
	filters: [
		{
			fieldname: "subcontractor",
			label: "Sub Contractor",
			fieldtype: "Link",
			options: "Supplier",
		},
		{
			fieldname: "month",
			label: "Month",
			fieldtype: "Select",
			options: [
				"January",
				"February",
				"March",
				"April",
				"May",
				"June",
				"July",
				"August",
				"September",
				"October",
				"November",
				"December",
			],
			default: new Date().toLocaleString("default", { month: "long" }),
			reqd: 1,
		},
		{
			fieldname: "year",
			label: "Year",
			fieldtype: "Select",
			options: ["2025", "2026", "2027", "2028"],
			default: new Date().getFullYear().toString(),
		},
		{
			fieldname: "project",
			label: "Project",
			fieldtype: "Link",
			options: "Project",
		},
	],
};
