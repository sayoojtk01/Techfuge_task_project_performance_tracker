/** @odoo-module **/
import { Component, useState, onMounted } from "@odoo/owl";
import rpc from "web.rpc";

export class ProjectPerformanceDashboard extends Component {
    setup() {
        this.state = useState({
            monthlyEfficiency: [],
            topEmployees: [],
        });

        onMounted(async () => {
            // Fetch project efficiency by month
            const efficiencyData = await rpc.query({
                model: 'project.project',
                method: 'get_monthly_efficiency',
            });
            this.state.monthlyEfficiency = efficiencyData;

            // Fetch top 5 employees
            const topEmpData = await rpc.query({
                model: 'account.analytic.line',
                method: 'get_top_employees',
            });
            this.state.topEmployees = topEmpData;
        });
    }
}
ProjectPerformanceDashboard.template = "project_performance_tracker.dashboard_template";
