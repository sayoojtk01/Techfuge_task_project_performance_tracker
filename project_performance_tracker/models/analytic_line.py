# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from collections import defaultdict


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    is_billable = fields.Boolean(string="Is Billable", default=True)
    complexity_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string="Complexity Level", default='low')
    efficiency_weight = fields.Float(string="Efficiency Weight", compute="_compute_efficiency_weight", store=True)

    @api.depends('complexity_level')
    def _compute_efficiency_weight(self):
        mapping = {'low': 1.0, 'medium': 1.25, 'high': 1.5}
        for line in self:
            line.efficiency_weight = mapping.get(line.complexity_level, 1.0)

    # def get_top_employees(self):
    #     """For dashboard"""
    #     self.env.cr.execute("""
    #         SELECT
    #             emp.name,
    #             SUM(line.unit_amount * CASE line.complexity_level
    #                 WHEN 'Low' THEN 1
    #                 WHEN 'Medium' THEN 1.25
    #                 WHEN 'High' THEN 1.5
    #                 ELSE 1 END) AS weighted_hours
    #         FROM account_analytic_line line
    #         JOIN hr_employee emp ON line.employee_id = emp.id
    #         GROUP BY emp.name
    #         ORDER BY weighted_hours DESC
    #         LIMIT 5;
    #     """)
    #     rows = self.env.cr.fetchall()
    #     return [{'name': name, 'weighted_hours': round(hours, 2)} for name, hours in rows]
