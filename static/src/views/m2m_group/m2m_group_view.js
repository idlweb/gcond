/** @odoo-module */

import { registry } from "@web/core/registry";
import { standardViewProps } from "@web/views/standard_view_props";
import { M2mGroupController } from "./m2m_group_controller";
import { M2mGroupRenderer } from "./m2m_group_renderer";

export const m2mGroupView = {
    type: "m2m_group",
    display_name: "Author",
    icon: "fa-id-card-o",
    multiRecord: true,
    Controller: M2mGroupController,
    Renderer: M2mGroupRenderer,
    props: {
        ...standardViewProps,
    },
};

registry.category("views").add("m2m_group", m2mGroupView);
