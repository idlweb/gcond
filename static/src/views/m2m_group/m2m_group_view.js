/** @odoo-module */

import { registry } from "@web/core/registry";
import { M2mGroupController } from "./m2m_group_controller";
import { M2mGroupRenderer } from "./m2m_group_renderer";

// Rimuoviamo la proprietà 'type' che causa il crash in Odoo 18
export const m2mGroupView = {
    display_name: "M2M Group",
    icon: "fa-id-card-o",
    multiRecord: true,
    Controller: M2mGroupController,
    Renderer: M2mGroupRenderer,

    // In Odoo 18, la gestione dei props è stata semplificata
    props: (genericProps, view) => {
        return {
            ...genericProps,
            Model: view.Model,
            Renderer: M2mGroupRenderer,
            // Usiamo il getter corretto per gli attributi dell'architettura
            buttonTemplate: genericProps.arch.getAttribute("button_template"),
        };
    },
};

// Quando aggiungiamo al registro, il nome della categoria ("m2m_group") 
// funge già da identificatore del tipo di vista.
registry.category("views").add("m2m_group", m2mGroupView);