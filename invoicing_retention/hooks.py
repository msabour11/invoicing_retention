app_name = "invoicing_retention"
app_title = "Invoicing Retention"
app_publisher = "Mohamed AbdElsabour"
app_description = "Retention Invoicing for Erpnext Accounting"
app_email = "eng.mohammed.sabour@gmail.com"
app_license = "mit"


required_apps = ["frappe", "erpnext"]
doctype_js = {"Sales Invoice": "public/js/retention_sales_invoice.js"}
doc_events = {
    "Sales Invoice": {
        "on_submit": [
            "invoicing_retention.overrides.retention_sales_invoice.after_submit",
        ],
        "on_cancel": [
            "invoicing_retention.overrides.retention_sales_invoice.on_cancel",
        ],
    }
}

fixtures = [
    {"dt": "Custom Field", "filters": [["module", "in", "Invoicing Retention"]]}
]

accounting_dimension_doctypes = ["Sales Invoice Retention"]
