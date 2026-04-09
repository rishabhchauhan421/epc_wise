# Copyright (c) 2026, EPC Wise
import frappe
import calendar
from datetime import date, timedelta
from frappe.utils import getdate, flt

def execute(filters=None):
    filters = filters or {}
    if not filters.get("month") or not filters.get("year"):
        return [], []

    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Sub Contractor", "fieldname": "subcontractor", "fieldtype": "Link", "options": "Supplier", "width": 150},
        {"label": "Name", "fieldname": "supplier_name", "width": 150},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 120},
        {"label": "Std Days", "fieldname": "standard_days", "fieldtype": "Int", "width": 80},
        {"label": "Days Worked", "fieldname": "days_worked", "fieldtype": "Int", "width": 100},
        {"label": "Total Sundays", "fieldname": "total_sundays", "fieldtype": "Int", "width": 100},
        {"label": "Sundays Worked", "fieldname": "sunday_worked", "fieldtype": "Int", "width": 110},
        {"label": "Holidays", "fieldname": "holidays_count", "fieldtype": "Int", "width": 90},
        {"label": "Deductions", "fieldname": "deductions", "fieldtype": "Int", "width": 90},
        {"label": "Payable Days", "fieldname": "total_payable_days", "fieldtype": "Float", "width": 110},
        {"label": "Contract Amt", "fieldname": "monthly_work_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Basic Amt", "fieldname": "basic_earned", "fieldtype": "Currency", "width": 120},
        {"label": "OT Hours", "fieldname": "ot_hours", "fieldtype": "Float", "width": 80},
        {"label": "OT Amt", "fieldname": "ot_amount", "fieldtype": "Currency", "width": 110},
        {"label": "Meals", "fieldname": "meals", "fieldtype": "Currency", "width": 100},
        {"label": "TPP Deduction", "fieldname": "tpp_deduction", "fieldtype": "Currency", "width": 110},
        {"label": "Net Payable", "fieldname": "net_payable", "fieldtype": "Currency", "width": 130, "is_bold": 1},
    ]

def get_data(filters):
    data = []

    # Get month details
    month_name = filters.get("month")
    year = int(filters.get("year"))
    month_map = {m: i for i, m in enumerate(calendar.month_name) if m}
    m_idx = month_map.get(month_name)

    start_date = date(year, m_idx, 1)
    standard_days = calendar.monthrange(year, m_idx)[1]
    end_date = date(year, m_idx, standard_days)

    # Fetch global holiday count for the month
    holidays = frappe.get_all("Holiday",
        filters={"parent": "Subcontractor HL", "holiday_date": ["between", [start_date, end_date]]})
    holidays_count = len(holidays)

    # Get Meal Rate from Settings
    meal_rate = flt(frappe.db.get_single_value("EPC Wise Settings", "overtime_meal_extra_amount"))

    # Fetch Subcontractors
    sc_filters = {"supplier_group": "Sub Contractor"}
    if filters.get("subcontractor"):
        sc_filters["name"] = filters["subcontractor"]

    subcontractors = frappe.get_all("Supplier", filters=sc_filters, fields=["name", "supplier_name"])

    for sc in subcontractors:
        # 1. Fetch Timesheets
        timesheets = frappe.get_all("Subcontractor Timesheet",
            filters={"subcontractor": sc.name, "work_date": ["between", [start_date, end_date]], "docstatus": 1},
            fields=["work_date", "ot_hours", "overtime_meal_extra"])

        worked_dates = {getdate(ts.work_date) for ts in timesheets}

        # 2. Fetch TPP (Contract and Deduction)
        tpp = frappe.db.get_value("Subcontractor TPP",
            {"subcontractor": sc.name, "month": month_name, "year": filters.get("year"), "docstatus": 1},
            ["project", "monthly_work_amount", "tppamount"], as_dict=1)

        if filters.get("project") and (not tpp or tpp.project != filters.get("project")):
            continue

        contract_amt = flt(tpp.monthly_work_amount) if tpp else 0
        tpp_deduction = flt(tpp.tppamount) if (tpp and flt(tpp.tppamount) > 0) else 0

        # 3. Attendance Logic
        days_worked = len(worked_dates)
        sunday_worked = sum(1 for d in worked_dates if d.weekday() == 6)

        total_sundays = 0
        deductions = 0
        curr = start_date
        while curr <= end_date:
            if curr.weekday() == 6: # Sunday
                total_sundays += 1
                sat, mon = curr - timedelta(days=1), curr + timedelta(days=1)
                # Deduction: If Sat, Sun, Mon consecutive dates have no records
                if curr not in worked_dates and sat not in worked_dates and mon not in worked_dates:
                    deductions += 1
            curr += timedelta(days=1)

        # 4. Final Calculations
        payable_days = days_worked + total_sundays + holidays_count - deductions
        basic_amt = (contract_amt * payable_days) / standard_days

        ot_hour_rate = contract_amt / (standard_days * 8)
        total_ot_hours = sum(flt(ts.ot_hours) for ts in timesheets)
        ot_amt = total_ot_hours * ot_hour_rate

        # Meal logic: OT > 2 hours AND checkmark is active
        meals_amt = sum(meal_rate for ts in timesheets if flt(ts.ot_hours) > 2 and ts.overtime_meal_extra)

        total_payable = basic_amt + ot_amt + meals_amt
        net_payable = total_payable - tpp_deduction

        data.append({
            "subcontractor": sc.name,
            "supplier_name": sc.supplier_name,
            "project": tpp.project if tpp else "",
            "standard_days": standard_days,
            "days_worked": days_worked,
            "total_sundays": total_sundays,
            "sunday_worked": sunday_worked,
            "holidays_count": holidays_count,
            "deductions": deductions,
            "total_payable_days": payable_days,
            "monthly_work_amount": contract_amt,
            "basic_earned": basic_amt,
            "ot_hours": total_ot_hours,
            "ot_amount": ot_amt,
            "meals": meals_amt,
            "tpp_deduction": tpp_deduction,
            "net_payable": net_payable
        })

    return data
