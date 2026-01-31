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

        # Changed label to be specific
        {"label": "Days Worked", "fieldname": "days_worked", "fieldtype": "Float", "width": 100},
        {"label": "Sundays Worked", "fieldname": "sunday_worked", "fieldtype": "Int", "width": 110},
        {"label": "Nights Worked", "fieldname": "nights_worked", "fieldtype": "Int", "width": 100},

        {"label": "Total Payable Days", "fieldname": "total_payable_days", "fieldtype": "Float", "width": 130},

        {"label": "Monthly Rate", "fieldname": "monthly_work_amount", "fieldtype": "Currency", "width": 140},
        {"label": "Rate / Day", "fieldname": "per_day_amount", "fieldtype": "Currency", "width": 100},
        {"label": "Basic Earned", "fieldname": "basic_earned", "fieldtype": "Currency", "width": 140},

        {"label": "OT Hours", "fieldname": "ot_hours", "fieldtype": "Float", "width": 100},
        {"label": "OT Rate", "fieldname": "ot_hour_rate", "fieldtype": "Currency", "width": 100},
        {"label": "OT Amount", "fieldname": "ot_amount", "fieldtype": "Currency", "width": 120},

        {"label": "Meals", "fieldname": "meals", "fieldtype": "Currency", "width": 120},
        {"label": "Less: TPP Amount", "fieldname": "tpp_deduction", "fieldtype": "Currency", "width": 140},

        {"label": "Net Payable", "fieldname": "net_payable", "fieldtype": "Currency", "width": 140, "is_bold": 1},
    ]


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def month_number(month):
    return {
        "January": 1, "February": 2, "March": 3,
        "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9,
        "October": 10, "November": 11, "December": 12
    }.get(month)


def get_month_date_range(month, year):
    m = month_number(month)
    y = int(year)
    last_day = calendar.monthrange(y, m)[1]
    return date(y, m, 1), date(y, m, last_day)


# ---------------------------------------------------------------------
# DATA FETCHING
# ---------------------------------------------------------------------

def get_subcontractors(filters):
    cond = {"supplier_group": "Sub Contractor"}
    if filters.get("subcontractor"):
        cond["name"] = filters["subcontractor"]

    return frappe.get_all(
        "Supplier",
        filters=cond,
        fields=["name", "supplier_name"]
    )


def get_timesheets(subcontractor, start, end):
    return frappe.get_all(
        "Subcontractor Timesheet",
        filters={
            "subcontractor": subcontractor,
            "work_date": ["between", [start, end]]
        },
        fields=["work_date", "ot_hours", "overtime_meal_extra"]
    )


def get_tpp(subcontractor, month, year):
    tpp_list = frappe.get_all(
        "Subcontractor TPP",
        filters={
            "subcontractor": subcontractor,
            "month": month,
            "year": year
        },
        fields=["project", "monthly_work_amount", "tppamount"],
        limit=1
    )
    return tpp_list[0] if tpp_list else None


def get_month_holidays(start, end):
    holidays = frappe.get_all(
        "Holiday",
        filters={
            "parent": "Subcontractor HL",
            "holiday_date": ["between", [start, end]]
        },
        fields=["holiday_date"]
    )
    return {getdate(h.holiday_date) for h in holidays}


# ---------------------------------------------------------------------
# BUSINESS LOGIC
# ---------------------------------------------------------------------

def calculate_attendance_and_pay_days(timesheets, holidays, start, end):
    """
    Returns: (worked_days_count, actual_sundays_worked, total_payable_days)
    """

    # 1. Identify Worked Dates
    worked_dates = {getdate(ts.work_date) for ts in timesheets} if timesheets else set()

    # 2. Count "Actual Sundays Worked" (Strictly for the report column)
    actual_sundays_worked = sum(1 for d in worked_dates if d.weekday() == 6)

    # 3. Determine "Payable Base"
    # Union of Worked Days and Holidays to avoid double counting if someone works on a holiday
    unique_payable_dates = worked_dates.union(holidays)
    base_payable_days = len(unique_payable_dates)

    # 4. Calculate "Sandwich Sundays" (Payable but NOT worked)
    sandwich_payable_sundays = 0

    current_date = start
    while current_date <= end:
        if current_date.weekday() == 6: # Sunday

            # If Sunday was already worked, it's in 'base_payable_days'.
            # We only care here about adding it if they DIDN'T work but deserve pay.
            if current_date not in worked_dates:

                saturday = current_date - timedelta(days=1)
                monday = current_date + timedelta(days=1)

                # Check Saturday status
                sat_present = False
                if saturday < start:
                    sat_present = True # Assume present if previous month
                else:
                    sat_present = (saturday in worked_dates) or (saturday in holidays)

                # Check Monday status
                mon_present = False
                if monday > end:
                    mon_present = True # Assume present if next month
                else:
                    mon_present = (monday in worked_dates) or (monday in holidays)

                # Sandwich Rule: Paid unless absent on BOTH sides
                if sat_present or mon_present:
                    sandwich_payable_sundays += 1

        current_date += timedelta(days=1)

    # Total Pay = Worked + Holidays + Sandwich Sundays (non-worked)
    total_payable_days = base_payable_days + sandwich_payable_sundays

    return len(worked_dates), actual_sundays_worked, total_payable_days


def calculate_ot(timesheets):
    return sum(flt(ts.ot_hours) for ts in timesheets)


def calculate_meals(timesheets):
    meal_days = 0
    for ts in timesheets:
        if flt(ts.ot_hours) > 2 and ts.overtime_meal_extra:
            meal_days += 1

    meal_rate = flt(frappe.get_cached_value("EPC Wise Settings", None, "overtime_meal_extra_amount"))
    return meal_days * meal_rate


# ---------------------------------------------------------------------
# MAIN DATA GENERATION
# ---------------------------------------------------------------------

def get_data(filters):
    data = []
    month = filters.get("month")
    year = filters.get("year")

    start_date, end_date = get_month_date_range(month, year)
    month_holidays = get_month_holidays(start_date, end_date)
    subcontractors = get_subcontractors(filters)

    for sc in subcontractors:
        timesheets = get_timesheets(sc.name, start_date, end_date)
        tpp = get_tpp(sc.name, month, year)

        if filters.get("project"):
            if not tpp or tpp.project != filters.get("project"):
                continue

        monthly_rate = flt(tpp.monthly_work_amount) if tpp else 0
        tpp_deduction = flt(tpp.tppamount) if tpp else 0
        project_name = tpp.project if tpp else None

        # --- UPDATED UNPACKING ---
        worked_count, actual_sundays_worked, total_payable_days = calculate_attendance_and_pay_days(
            timesheets, month_holidays, start_date, end_date
        )
        # -------------------------

        per_day_amount = monthly_rate / 30 if monthly_rate else 0
        basic_earned = per_day_amount * total_payable_days

        ot_hours = calculate_ot(timesheets)
        ot_hour_rate = per_day_amount / 8 if per_day_amount else 0
        ot_amount = ot_hours * ot_hour_rate

        meals = calculate_meals(timesheets)

        net_payable = (basic_earned + ot_amount + meals) - tpp_deduction

        data.append({
            "subcontractor": sc.name,
            "supplier_name": sc.supplier_name,
            "project": project_name,

            "days_worked": worked_count,
            "sunday_worked": actual_sundays_worked, # Now strictly worked
            "nights_worked": 0,
            "total_payable_days": total_payable_days,

            "monthly_work_amount": monthly_rate,
            "per_day_amount": per_day_amount,
            "basic_earned": basic_earned,

            "ot_hours": ot_hours,
            "ot_hour_rate": ot_hour_rate,
            "ot_amount": ot_amount,

            "meals": meals,
            "tpp_deduction": tpp_deduction,
            "net_payable": net_payable
        })

    return data
