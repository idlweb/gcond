/** @odoo-module */

import { registry } from "@web/core/registry";
import { M2mGroupController } from "./m2m_group_controller";
import { M2mGroupRenderer } from "./m2m_group_renderer";

export const m2mGroupView = {
    // In Odoo 18, 'type' deve corrispondere a una categoria di vista valida
    // Se la tua vista m2m_group si comporta come una lista, usa "list".
    // Se è totalmente custom, assicurati che sia registrata correttamente.
    type: "list",
    display_name: "M2M Group",
    icon: "fa-id-card-o",
    multiRecord: true,
    Controller: M2mGroupController,
    Renderer: M2mGroupRenderer,

    props: (genericProps, view) => {
        return {
            ...genericProps,
            // Rimuoviamo riferimenti a view.Model se causa undefined
            Renderer: M2mGroupRenderer,
            buttonTemplate: genericProps.arch.getAttribute("button_template"),
        };
    },
};

// Registrazione
registry.category("views").add("m2m_group", m2mGroupView);