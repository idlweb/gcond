/** @odoo-module */

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, onMounted, onWillUnmount, useRef, useEffect } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";

export class GaugeField extends Component {
    static template = "gcond.GaugeField";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.chartRef = useRef("chart");
        this.chartInstance = null;

        onMounted(() => {
            this.renderChart();
        });

        useEffect(() => {
            this.renderChart();
        }, () => [this.props.record.data[this.props.name]]);

        onWillUnmount(() => {
            if (this.chartInstance) {
                this.chartInstance.destroy();
                this.chartInstance = null;
            }
        });
    }

    async renderChart() {
        if (!this.chartRef.el) return;

        // Ensure Chart.js is loaded (if not globally available)
        // Note: 'web.assets_backend' usually includes it, but checking logic is good.
        // For Odoo 18, we might need to rely on global 'Chart' or import it if bundled.
        // Assuming global 'Chart' for now as per legacy code. However, best practice is to ensure it is defined.

        if (typeof Chart === 'undefined') {
            await loadBundle("web.chartjs"); // Try to load if missing
        }

        const ctx = this.chartRef.el.getContext("2d");
        const value = this.props.record.data[this.props.name] || 0;

        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        this.chartInstance = new Chart(ctx, {
            type: "gauge", // Ensure chartjs-gauge is loaded
            data: {
                datasets: [{
                    data: [100],
                    value: value,
                    backgroundColor: ["green", "yellow", "orange", "red"],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: this.props.record.data.display_name || "Gauge" // Fallback title
                },
                layout: {
                    padding: { bottom: 30 }
                },
                needle: {
                    radiusPercentage: 2,
                    widthPercentage: 3.2,
                    lengthPercentage: 80,
                    color: "rgba(0, 0, 0, 1)"
                },
                valueLabel: {
                    formatter: Math.round
                }
            }
        });
    }
}

export const gaugeField = {
    component: GaugeField,
    supportedTypes: ["float", "integer"],
};

registry.category("fields").add("gauge_field", gaugeField);
