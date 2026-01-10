/** @odoo-module */

import { registry } from "@web/core/registry";
import { M2mGroupController } from "./m2m_group_controller";
import { M2mGroupRenderer } from "./m2m_group_renderer";

export const m2mGroupView = {
    type: "m2m_group",
    display_name: "M2M Group",
    icon: "fa-id-card-o",
    multiRecord: true,
    Controller: M2mGroupController,
    Renderer: M2mGroupRenderer,

    props: (genericProps, view) => {
        const { arch, relatedModels, resModel } = genericProps;
        return {
            ...genericProps,
            Model: view.Model,
            Renderer: M2mGroupRenderer,
            buttonTemplate: arch.getAttribute("button_template"),
        };
    },
};

registry.category("views").add("m2m_group", m2mGroupView);
