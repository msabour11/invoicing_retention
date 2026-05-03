import frappe
from frappe.utils import flt, nowdate
from frappe import _


def validate(doc, method):
    # Calculate and store total retention for reference
    total_retention = 0
    for d in doc.retention:
        total_retention += flt(d.retention_amount)
    doc.total_retention_amount = total_retention


#  Sales Invoice Retention GL Entry After Submit


def after_submit(doc, method):
    make_retention_gl_entries(doc, method)


def make_retention_gl_entries(doc, method=None):
    if not doc.retention:
        return

    # Check if already posted (prevent duplicate on resubmit)
    existing = frappe.db.get_value(
        "GL Entry",
        {
            "voucher_type": "Sales Invoice",
            "voucher_no": doc.name,
            "is_retention_entry": 1,
        },
        "name",
    )

    if existing:
        return

    gl_entries = []

    for row in doc.retention:
        if flt(row.retention_amount) <= 0:
            continue

        # Debit Entry - Customer Account (Debit To)
        gl_entries.append(
            doc.get_gl_dict(
                {
                    "account": doc.debit_to,
                    "debit": flt(row.retention_amount),
                    "credit": 0,
                    "against": row.account_head,
                    "cost_center": doc.cost_center,
                    "party_type": "Customer",
                    "party": doc.customer,
                    "is_retention_entry": 1,
                    "remarks": _("Retention Debit - Invoice {0}").format(doc.name),
                }
            )
        )

        # Credit Entry - Retention Account
        gl_entries.append(
            doc.get_gl_dict(
                {
                    "account": row.account_head,
                    "debit": 0,
                    "credit": flt(row.retention_amount),
                    "against": doc.debit_to,
                    "cost_center": doc.cost_center,
                    "is_retention_entry": 1,
                    "remarks": _("Retention Credit - Invoice {0} - Rate: {1}%").format(
                        doc.name, row.retention_rate
                    ),
                }
            )
        )

    # Post GL Entries
    if gl_entries:
        from erpnext.accounts.general_ledger import make_gl_entries

        make_gl_entries(gl_entries, cancel=(method == "on_cancel"))

        frappe.msgprint(
            _("Retention GL Entries created for amount: {0}").format(
                sum(flt(d.retention_amount) for d in doc.retention)
            ),
            alert=True,
        )


# On Cancel


def on_cancel(doc, method):
    cancel_retention_gl_entries(doc)


def cancel_retention_gl_entries(doc):
    # Get all retention GL entries for this invoice
    gl_entries = frappe.db.get_all(
        "GL Entry",
        filters={
            "voucher_type": "Sales Invoice",
            "voucher_no": doc.name,
            "is_retention_entry": 1,
        },
        fields=["name", "account", "debit", "credit", "against"],
    )

    if not gl_entries:
        return

    # Create reverse entries
    reverse_entries = []
    for gle in gl_entries:
        reverse_entries.append(
            doc.get_gl_dict(
                {
                    "account": gle.account,
                    "debit": flt(gle.credit),  # Reverse debit/credit
                    "credit": flt(gle.debit),
                    "against": gle.against,
                    "cost_center": doc.cost_center,
                    "is_retention_entry": 1,
                    "is_cancelled": 1,
                    "remarks": _("Retention Entry Cancelled - Invoice {0}").format(
                        doc.name
                    ),
                }
            )
        )

    if reverse_entries:
        from erpnext.accounts.general_ledger import make_gl_entries

        make_gl_entries(reverse_entries, cancel=True)
