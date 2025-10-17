# -*- coding: utf-8 -*-

{
    "name": "Project Performance Tracker",
    "version": "1.0.0",
    "summary": "Project performance track, push weekly reports to external api and alert low-performing projects",
    "description": "Extends project and timesheet models, computes performance , sends alerts and pushes weekly summaries to external API. Provides settings and report wizard.",
    "category": "Project",
    "author": "Sayooj t k",
    "depends": ["project","report_xlsx","hr_timesheet", "mail", "base"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/performance_alert_mail_template.xml",
        "data/project_performance_cron.xml",
        "report/performance_report_action.xml",
        "wizard/performance_wizard_view.xml",
        "views/project_project_view.xml",
        "views/analytic_line_view.xml",
        "views/res_config_settings.xml",
        "views/menus.xml",
        # "views/project_performance_dashboard_templates.xml",
        # "views/dashboard_menu_action.xml",

    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'project_performance_tracker/static/src/components/dashboard.js',
    #     ],
    # },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
