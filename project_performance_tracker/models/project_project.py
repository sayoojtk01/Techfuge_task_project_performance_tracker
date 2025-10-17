# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from datetime import datetime
from collections import defaultdict

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = "project.project"

    performance_score = fields.Float(string="Performance Score", readonly=True)
    billable_hours = fields.Float(string="Billable Hours", compute="_compute_billable_nonbillable", store=True)
    non_billable_hours = fields.Float(string="Non Billable Hours", compute="_compute_billable_nonbillable", store=True)
    project_efficiency = fields.Float(string="Project Efficiency %", compute="_compute_billable_nonbillable",
                                      store=True)
    external_report_id = fields.Char(string="External Report ID", readonly=True)

    @api.depends('timesheet_ids.unit_amount', 'timesheet_ids.is_billable', 'timesheet_ids.efficiency_weight')
    def _compute_billable_nonbillable(self):
        for project in self:
            timesheets = project.timesheet_ids.filtered(lambda l: l.project_id.id == project.id)
            billable = sum(l.unit_amount for l in timesheets.filtered(lambda l: l.is_billable))
            non_billable = sum(l.unit_amount for l in timesheets.filtered(lambda l: not l.is_billable))
            total = billable + non_billable
            project.billable_hours = billable
            project.non_billable_hours = non_billable
            project.project_efficiency = (billable / total * 100) if total else 0.0

    def compute_performance_score(self):
        """ Compute and return performance_score for this project """
        for project in self:
            timesheets = project.timesheet_ids
            total_hours = sum(line.unit_amount for line in timesheets)
            if not total_hours:
                project.performance_score = 0.0
                continue
            weighted_sum = sum((line.unit_amount or 0.0) * (line.efficiency_weight or 1.0) for line in timesheets)
            score = weighted_sum / total_hours
            project.performance_score = score
        return True

    def cron_compute_and_report(self):
        """Weekly Calculation and pushing to external api and mail"""

        # import here to avoid import at module load if requests not available
        import json, requests
        from requests.exceptions import RequestException

        IRConfig = self.env['ir.config_parameter'].sudo()
        threshold = float(IRConfig.get_param('project_performance_tracker.performance_alert_threshold') or 0.0)
        recipient_ids = IRConfig.get_param('project_performance_tracker.alert_recipient_ids') or ''
        recipients = []
        if recipient_ids:
            try:
                # recipients users seppeartion from recipient_ids
                recipients = [int(x) for x in recipient_ids.split(',') if x.strip()]
            except Exception:
                recipients = []

        # Fetch recipients users
        recipients_users = self.env['res.users'].browse(recipients)

        # Fetch end point and headers
        endpoint = IRConfig.get_param(
            'project_performance_tracker.external_endpoint') or 'https://localhost:8069/api/project/report'
        headers = {'Content-Type': 'application/json'}

        projects = self.search([('active', '=', True)])
        for proj in projects:
            # Fetch data project wise
            proj.compute_performance_score()
            data = {
                'name': proj.name,
                'total_hours': sum(line.unit_amount for line in proj.timesheet_ids),
                'efficiency': proj.project_efficiency,
                'score': proj.performance_score,
            }

            # push to external API
            try:
                response_data = requests.post(endpoint, json=data, headers=headers, verify=False, timeout=10)
                if response_data.ok:
                    # try to parse json and store id
                    try:
                        j = response_data.json()
                        external_report_id = j.get('id') or j.get('report_id') or None
                        if external_report_id:
                            proj.external_report_id = str(external_report_id) if external_report_id else None

                    except Exception:
                        # Manage Exception case based on conditions store failed datas or send to other apis
                        print("[Request failed with status for project]:")
                else:
                    # Manage failed case based on conditions store failed datas or send to other apis
                    print("[Request failed with status for project]:")

            except RequestException as error:
                # Manage Exception case based on conditions store failed datas or send to other apis
                print("[Request failed with status for project]:", error)

            # if below threshold -> send mail
            if threshold and proj.performance_score < threshold and recipients_users:
                template = self.env.ref('project_performance_tracker.mail_template_low_performance',
                                        raise_if_not_found=False)
                if template:
                    try:
                        template.sudo().with_context(project_score=proj.performance_score).send_mail(proj.id,
                                                                                                     force_send=True,
                                                                                                     raise_exception=False)
                    except Exception as e:
                        # to avoid cron crash
                        _logger = self.env['ir.logging'].sudo()
                        _logger.create({
                            'name': 'project_performance_tracker send_mail error',
                            'type': 'server',
                            'dbname': self.env.cr.dbname,
                            'message': str(e),
                            'level': 'ERROR',
                            'path': 'project_performance_tracker.project',
                            'line': '0',
                        })
        return True


    # def get_monthly_efficiency(self):
    #     """ For dashboard"""
    #     results = []
    #     self.env.cr.execute("""
    #         SELECT
    #             to_char(date_trunc('month', line.date), 'YYYY-MM') AS month,
    #             SUM(line.unit_amount * CASE line.complexity_level
    #                 WHEN 'Low' THEN 1
    #                 WHEN 'Medium' THEN 1.25
    #                 WHEN 'High' THEN 1.5
    #                 ELSE 1 END) / SUM(line.unit_amount) * 100 AS efficiency
    #         FROM account_analytic_line line
    #         JOIN project_project proj ON line.project_id = proj.id
    #         GROUP BY month
    #         ORDER BY month;
    #     """)
    #     rows = self.env.cr.fetchall()
    #     for month, efficiency in rows:
    #         results.append({'month': month, 'efficiency': round(efficiency, 2)})
    #     return results
