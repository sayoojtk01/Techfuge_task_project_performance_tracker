# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectPerformanceReportWizard(models.TransientModel):
    _name = 'project.performance.report.wizard'
    _description = 'Project Performance Report Wizard'

    project_ids = fields.Many2many('project.project', string="Projects")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    report_file = fields.Binary("Report File", readonly=True)
    report_filename = fields.Char("Filename", readonly=True)

    def generate_xlsx(self):
        """ Report generation based on report_xlsx module"""
        return self.env.ref('project_performance_tracker.action_report_project_performance_xlsx').report_action(self)
