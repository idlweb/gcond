
# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class Saldo(http.Controller):
    @http.route('/mio-conto', type='http', auth="user", website=True)
    def gcond_saldo(self):
         return request.render(
            'gcond.mio-conto', {
                'saldo': request.env['account.move'].search([]),
            })

    @http.route('/books/submit_pag', type='http', auth="user", website=True)
    def saldo_pago(self, **post):
        if post.get('book_id'):
            conto_id = int(post.get('conto_id'))
            pagamento = post.get('issue_description')
            request.env['account.move'].sudo().create({
                'id': conto_id,
                'name': pagamento,
                #'submitted_by': request.env.user.id
            })
            return request.redirect('/saldo/submit_pag?submitted=1')

        return request.render('gcond.conto_pag_form', {
            'saldo': request.env['account.move'].search([]),
            'submitted': post.get('submitted', False)
        })