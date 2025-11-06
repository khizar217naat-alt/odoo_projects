import re
from odoo import http
from odoo.http import request

class PortalResetPassword(http.Controller):

    @http.route('/portal/reset_password', type='http', auth='public', website=True, csrf=False)
    def portal_reset_password(self, **post):
        error = None
        if post.get('email'):
            user = request.env['res.users'].sudo().search([
                ('login', '=', post.get('email')),
                ('share', '=', True)
            ], limit=1)

            if user:
                return request.render('portal_reset_password.portal_set_password_form', {
                    'portal_user_id': user.id,
                    'user_email': user.login,
                })
            else:
                error = "Email not found"

        return request.render('portal_reset_password.portal_reset_password_form', {
            'error': error,
        })

    @http.route('/portal/set_password', type='http', auth='public', website=True, csrf=False)
    def portal_set_password(self, **post):
        user_id = post.get('portal_user_id')
        new_password = post.get('new_password')
        confirm_password = post.get('confirm_password')
        error = None

        if not user_id:
            return request.render('portal_reset_password.portal_reset_password_form', {
                'error': "Invalid user.",
            })

        user = request.env['res.users'].sudo().browse(int(user_id))

        if not user.exists():
            return request.render('portal_reset_password.portal_reset_password_form', {
                'error': "User not found.",
            })

        # Validate password strength
        if not new_password or len(new_password) < 8:
            error = "Password must be at least 8 characters long."
        elif new_password != confirm_password:
            error = "Passwords do not match."

        if error:
            return request.render('portal_reset_password.portal_set_password_form', {
                'portal_user_id': user.id,
                'user_email': user.login,
                'error': error,
            })

        # Save password
        user.sudo().password = new_password

        return request.render('portal_reset_password.portal_reset_password_done', {
            'user_email': user.login,
        })

class OverrideResetPassword(http.Controller):
    @http.route('/web/reset_password', type='http', auth='public', website=True, csrf=False)
    def redirect_reset_password(self, **kw):
        return request.redirect('/portal/reset_password')