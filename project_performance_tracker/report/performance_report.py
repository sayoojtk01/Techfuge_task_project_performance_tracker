# -*- coding: utf-8 -*-
from odoo import models


class ProjectPerformanceXlsxReport(models.AbstractModel):
    """ Report generation based on report_xlsx module"""

    _name = 'report.project_performance_tracker.project_performance_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        """ Excel format """
        worksheet = workbook.add_worksheet('Project Performance')
        bold = workbook.add_format({'bold': True})

        headers = ["Project Name", "Total Hours", "Billable Hours", "Non-billable Hours", "Performance Score",
                   "Efficiency %"]
        for col, h in enumerate(headers):
            worksheet.write(0, col, h, bold)

        projects = wizard.project_ids or self.env['project.project'].search([])
        row = 1
        totals = {'total_hours': 0.0, 'billable': 0.0, 'non_billable': 0.0}

        for project in projects:
            timesheets = self.env['account.analytic.line'].search([
                ('project_id', '=', project.id),
                ('date', '>=', wizard.date_from) if wizard.date_from else (),
                ('date', '<=', wizard.date_to) if wizard.date_to else ()
            ])

            total_hours = sum(ts.unit_amount for ts in timesheets)
            billable = sum(ts.unit_amount for ts in timesheets.filtered(lambda t: t.is_billable))
            non_billable = total_hours - billable
            weighted_sum = sum((ts.unit_amount or 0.0) * (ts.efficiency_weight or 1.0) for ts in timesheets)
            score = weighted_sum / total_hours if total_hours else 0.0
            efficiency = (billable / total_hours * 100) if total_hours else 0.0

            worksheet.write(row, 0, project.name)
            worksheet.write(row, 1, total_hours)
            worksheet.write(row, 2, billable)
            worksheet.write(row, 3, non_billable)
            worksheet.write(row, 4, score)
            worksheet.write(row, 5, efficiency)

            totals['total_hours'] += total_hours
            totals['billable'] += billable
            totals['non_billable'] += non_billable
            row += 1

        worksheet.write(row, 0, 'Totals', bold)
        worksheet.write(row, 1, totals['total_hours'], bold)
        worksheet.write(row, 2, totals['billable'], bold)
        worksheet.write(row, 3, totals['non_billable'], bold)
