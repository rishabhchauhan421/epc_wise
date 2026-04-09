# epc_wise/epc_wise/doctype/subcontractor_timesheet/subcontractor_timesheet.py
import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_hours, get_time, getdate, add_days

class SubcontractorTimesheet(Document):
    def validate(self):
        self.calculate_hours()

    def calculate_hours(self):
        if self.in_time and self.out_time:
            # Calculate total duration
            total = time_diff_in_hours(self.out_time, self.in_time)
            self.total_hours = total

            # Standard shift is 9 hours (9 AM - 6 PM)
            # Logic: If total hours > 9, then OT = Total - 9
            if total > 9:
                self.ot_hours = total - 9
            else:
                self.ot_hours = 0

    def before_insert(self):
        # Prefill Logic: Fetch the most recent record for this subcontractor
        last_ts = frappe.get_all("Subcontractor Timesheet",
            filters={"subcontractor": self.subcontractor},
            fields=["in_time", "out_time", "parent_project"],
            order_by="work_date desc",
            limit=1
        )
        if last_ts:
            self.in_time = last_ts[0].in_time
            self.out_time = last_ts[0].out_time
            self.parent_project = last_ts[0].parent_project
