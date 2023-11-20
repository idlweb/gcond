
# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class Main(http.Controller):
    @http.route('/mio-conto', type='http', auth="user", website=True)
    def gcond_saldo(self):
        return request.render(
            pass,
            )