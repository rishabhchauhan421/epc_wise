import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today

class OutgoingPaymentRequest(Document):
    def validate(self):
        # 1. Date Validation
        if getdate(self.due_date) <= getdate(today()):
            frappe.throw("Payment Due Date must be after today's date.")

        # 2. Attachment Validation
        if not self.no_bill_exists:
            attachments = frappe.get_all("File", filters={
                "attached_to_doctype": self.doctype,
                "attached_to_name": self.name
            })
            if not self.is_new() and not attachments:
                frappe.throw("Please attach a bill or check 'No bill exists'.")

    def before_save(self):
        # 3. Auto-Approval Logic based on Category
        if self.payment_category:
            needs_approval = frappe.db.get_value("Payment for Category",
                                                 self.payment_category,
                                                 "accounts_approval_needed")
            if not needs_approval:
                self.verified_by_accounts = 1
