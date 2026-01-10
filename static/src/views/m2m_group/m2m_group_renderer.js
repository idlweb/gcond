/** @odoo-module */

import { Component } from "@odoo/owl";

export class M2mGroupRenderer extends Component {
    static template = "gcond.M2mGroupRenderer";
    static props = {
        groups: { type: Object, optional: true },
    };
}
