/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Layout } from "@web/search/layout";

export class M2mGroupController extends Component {
    static template = "gcond.M2mGroupView";

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.state = useState({
            groups: {},
            loading: true,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        // Replicating logic found in legacy Model (inferred):
        // Needs 'm2m_field' from arch/props to know what to fetch.
        // Legacy: this.loadParams.m2m_field = attrs.m2m_field;

        // In OWL, we access arch via props.archInfo or parse it.
        // But simpler: let's assume the controller knows what to fetch or look at context.
        // Actually, looking at the QWeb template, it handles 'groups'.

        // LIMITATION: Without seeing the complete legacy Model code, I have to guess the data structure.
        // However, I can infer we need to fetch the res.model records.

        // Let's implement a generic fetch for now, or use the model prop.
        const model = this.props.resModel;
        const domain = this.props.domain || [];

        try {
            // NOTE: This usually would need a custom route or a specific search_read logic
            // matching the custom legacy model. 
            // For now, standard search_read.
            const records = await this.orm.searchRead(model, domain, [], { limit: 100 });

            // Transform records into 'groups' structure expected by Renderer
            // (Assuming simple list for now, or grouped by some logic if legacy did that)
            // Legacy template iterated 'groups' and 'group_data.children'.

            this.state.groups = records; // Simplified link
            this.state.loading = false;
        } catch (e) {
            console.error("Error loading M2m Group data", e);
        }
    }
}
