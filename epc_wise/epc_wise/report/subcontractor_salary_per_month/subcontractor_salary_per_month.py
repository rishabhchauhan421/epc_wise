# Copyright (c) 2026, EPC Wise
# For license information, please see license.txt

import frappe
import calendar
from datetime import date, timedelta
from frappe.utils import getdate, flt

def execute(filters=None):
    filters = filters or {}
    if not filters.get("month") or not filters.get("year"):
        return [], []

    return get_columns(), get_data(filters)

# ---------------------------------------------------------------------
# COLUMNS
# ---------------------------------------------------------------------

def get_columns():
    return [
        {"label": "Sub Contractor", "fieldname": "subcontractor", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": "Name", "fieldname": "supplier_name", "width": 180},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},

        {"label": "Standard Days", "fieldname": "standard_days", "fieldtype": "Int", "width": 100},
        {"label": "Days Worked", "fieldname": "days_worked", "fieldtype": "Int", "width": 100},
        {"label": "Sundays Worked", "fieldname": "sunday_worked", "fieldtype": "Int", "width": 110},
        {"label": "Total Sundays", "fieldname": "total_sundays", "fieldtype": "Int", "width": 100},
        {"label": "Holidays", "fieldname": "holidays_count", "fieldtype": "Int", "width": 100},
        {"label": "Deductions", "fieldname": "deductions", "fieldtype": "Int", "width": 100},

        {"label": "Total Payable Days", "fieldname": "total_payable_days", "fieldtype": "Float", "width": 130},

        {"label": "Contract Amount", "fieldname": "monthly_work_amount", "fieldtype": "Currency", "width": 130},
        {"label": "Basic Amount", "fieldname": "basic_earned", "fieldtype": "Currency", "width": 130},

        {"label": "OT Hours", "fieldname": "ot_hours", "fieldtype": "Float", "width": 90},
        {"label": "OT Amount", "fieldname": "ot_amount", "fieldtype": "Currency", "width": 110},

        {"label": "Meals", "fieldname": "meals", "fieldtype": "Currency", "width": 110},
        {"label": "Less: TPP", "fieldname": "tpp_deduction", "fieldtype": "Currency", "width": 110},

        {"label": "Net Payable", "fieldname": "net_payable", "fieldtype": "Currency", "width": 140, "is_bold": 1},
    ]

# ---------------------------------------------------------------------
# DATA FETCHING & HELPERS
# ---------------------------------------------------------------------

def month_number(month):
    return {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }.get(month)

def get_month_date_range(month, year):
    m = month_number(month)
    y = int(year)
    last_day = calendar.monthrange(y, m)[1]
    return date(y, m, 1), date(y, m, last_day), last_day

def get_subcontractors(filters):
    cond = {"supplier_group": "Sub Contractor"}
    if filters.get("subcontractor"):
        cond["name"] = filters["subcontractor"]
    return frappe.get_all("Supplier", filters=cond, fields=["name", "supplier_name"])

def get_timesheets(subcontractor, start, end):
    return frappe.get_all("Subcontractor Timesheet",
        filters={"subcontractor": subcontractor, "work_date": ["between", [start, end]]},
        fields=["work_date", "ot_hours", "overtime_meal_extra"])

def get_tpp(subcontractor, month, year):
    tpp_list = frappe.get_all("Subcontractor TPP",
        filters={"subcontractor": subcontractor, "month": month, "year": year},
        fields=["project", "monthly_work_amount", "tppamount"], limit=1)
    return tpp_list[0] if tpp_list else None

def get_month_holidays(start, end):
    holidays = frappe.get_all("Holiday",
        filters={"parent": "Subcontractor HL", "holiday_date": ["between", [start, end]]},
        fields=["holiday_date"])
    return {getdate(h.holiday_date) for h in holidays}

# ---------------------------------------------------------------------
# ATTENDANCE LOGIC (Absent Logic Removed)
# ---------------------------------------------------------------------

def calculate_attendance_and_pay_days(timesheets, holidays, start, end):
    worked_dates = {getdate(ts.work_date) for ts in timesheets} if timesheets else set()

    # 1. Days Worked
    days_worked = len(worked_dates)

    # 2. Sundays Worked (Count if record exists on Sunday)
    sunday_worked = sum(1 for d in worked_dates if d.weekday() == 6)

    # 3. Total Sundays in Month & Deductions (Consecutive Sat-Sun-Mon absence)
    total_sundays = 0
    deductions = 0
    curr = start
    while curr <= end:
        if curr.weekday() == 6: # Sunday
            total_sundays += 1
            sat = curr - timedelta(days=1)
            mon = curr + timedelta(days=1)

            # Deduction rule: No record for Sat, Sun, and Mon
            if (curr not in worked_dates and
                (sat < start or sat not in worked_dates) and
                (mon > end or mon not in worked_dates)):
                deductions += 1
        curr += timedelta(days=1)

    # 4. Total Payable Days: days_worked + sunday_worked + holidays - deductions
    holidays_count = len(holidays)
    total_payable_days = days_worked + sunday_worked + holidays_count - deductions

    return days_worked, sunday_worked, total_sundays, holidays_count, deductions, total_payable_days


def get_data(filters):
    data = []
    start_date, end_date, standard_days = get_month_date_range(filters.get("month"), filters.get("year"))
    month_holidays = get_month_holidays(start_date, end_date)
    subcontractors = get_subcontractors(filters)

    for sc in subcontractors:
        timesheets = get_timesheets(sc.name, start_date, end_date)
        tpp = get_tpp(sc.name, filters.get("month"), filters.get("year"))

        if filters.get("project") and (not tpp or tpp.project != filters.get("project")):
            continue

        contract_amount = flt(tpp.monthly_work_amount) if tpp else 0
        tpp_deduction = flt(tpp.tppamount) if tpp else 0

        # Attendance Calc
        worked_cnt, sun_worked_cnt, tot_sun, hol_cnt, deduct_cnt, total_payable = calculate_attendance_and_pay_days(
            timesheets, month_holidays, start_date, end_date
        )

        # Basic Amount = contract amount * payable days / standard days
        basic_earned = contract_amount * (total_payable / standard_days) if standard_days else 0

        # OT and Meals Logic
        # Per day rate for OT (Industry standard 30 day divisor)
        per_day_rate = contract_amount / 30
        ot_hours = sum(flt(ts.ot_hours) for ts in timesheets)
        ot_amount = ot_hours * (per_day_rate / 8 if per_day_rate else 0)

        meal_rate = flt(frappe.get_cached_value("EPC Wise Settings", None, "overtime_meal_extra_amount"))
        meals = sum(1 for ts in timesheets if flt(ts.ot_hours) > 2 and ts.overtime_meal_extra) * meal_rate

        net_payable = (basic_earned + ot_amount + meals) - tpp_deduction

        data.append({
            "subcontractor": sc.name,
            "supplier_name": sc.supplier_name,
            "project": tpp.project if tpp else None,
            "standard_days": standard_days,
            "days_worked": worked_cnt,
            "sunday_worked": sun_worked_cnt,
            "total_sundays": tot_sun,
            "holidays_count": hol_cnt,
            "deductions": deduct_cnt,
            "total_payable_days": total_payable,
            "monthly_work_amount": contract_amount,
            "basic_earned": basic_earned,
            "ot_hours": ot_hours,
            "ot_amount": ot_amount,
            "meals": meals,
            "tpp_deduction": tpp_deduction,
            "net_payable": net_payable
        })

    return data
