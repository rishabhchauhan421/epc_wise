app_name = "epc_wise"
app_title = "EPC Wise"
app_publisher = "Rishabh Chauhan"
app_description = "Manage EPC subcontractors, attendance, and payroll"
app_email = "rshbhchauhan@gmail.com"
app_license = "gpl-3.0"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "epc_wise",
# 		"logo": "/assets/epc_wise/logo.png",
# 		"title": "EPC Wise",
# 		"route": "/epc_wise",
# 		"has_permission": "epc_wise.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/epc_wise/css/epc_wise.css"
# app_include_js = "/assets/epc_wise/js/epc_wise.js"

# include js, css files in header of web template
# web_include_css = "/assets/epc_wise/css/epc_wise.css"
# web_include_js = "/assets/epc_wise/js/epc_wise.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "epc_wise/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "epc_wise/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "epc_wise.utils.jinja_methods",
# 	"filters": "epc_wise.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "epc_wise.install.before_install"
# after_install = "epc_wise.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "epc_wise.uninstall.before_uninstall"
# after_uninstall = "epc_wise.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "epc_wise.utils.before_app_install"
# after_app_install = "epc_wise.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "epc_wise.utils.before_app_uninstall"
# after_app_uninstall = "epc_wise.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "epc_wise.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"epc_wise.tasks.all"
# 	],
# 	"daily": [
# 		"epc_wise.tasks.daily"
# 	],
# 	"hourly": [
# 		"epc_wise.tasks.hourly"
# 	],
# 	"weekly": [
# 		"epc_wise.tasks.weekly"
# 	],
# 	"monthly": [
# 		"epc_wise.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "epc_wise.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "epc_wise.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "epc_wise.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "epc_wise.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["epc_wise.utils.before_request"]
# after_request = ["epc_wise.utils.after_request"]

# Job Events
# ----------
# before_job = ["epc_wise.utils.before_job"]
# after_job = ["epc_wise.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"epc_wise.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

