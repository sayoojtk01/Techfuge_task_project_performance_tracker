# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectPerformanceSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    performance_alert_threshold = fields.Float(string="Performance Alert Threshold (%)",
                                               config_parameter='project_performance_tracker.performance_alert_threshold')
    alert_recipients = fields.Many2many('res.users', string="Alert Recipients")

    external_endpoint = fields.Char(string="External API Endpoint", default='https://localhost:8069/api/project/report',
                                    config_parameter='project_performance_tracker.external_endpoint')

    @api.model
    def get_values(self):
        res = super().get_values()
        IrConfig = self.env['ir.config_parameter'].sudo()
        recipient_ids = IrConfig.get_param('project_performance_tracker.alert_recipient_ids', default='')
        res.update({
            'alert_recipients': [(6, 0, [int(x) for x in recipient_ids.split(',') if x])] if recipient_ids else [
                (6, 0, [])],
        })
        return res

    def set_values(self):
        super().set_values()
        IrConfig = self.env['ir.config_parameter'].sudo()
        if self.alert_recipients:
            IrConfig.set_param('project_performance_tracker.alert_recipient_ids',
                               ','.join(str(u.id) for u in self.alert_recipients))
        else:
            IrConfig.set_param('project_performance_tracker.alert_recipient_ids', '')
        if self.external_endpoint:
            IrConfig.set_param('project_performance_tracker.external_endpoint', self.external_endpoint)
