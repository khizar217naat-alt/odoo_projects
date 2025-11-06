# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleAddressAutofill(WebsiteSale):
    """
    Extend checkout values so that when a logged-in *portal* user
    reaches checkout, we prefill the form with their res.partner data.

    We do not affect Public users or Internal users (employees).
    """

    def _get_checkout_values(self, order, **kw):
        values = super()._get_checkout_values(order, **kw)

        user = request.env.user

        # Skip Public user and Internal users; target only portal users
        is_public = user._is_public()
        is_internal = user.has_group("base.group_user")
        if is_public or is_internal:
            return values

        partner = user.partner_id
        if not partner:
            return values

        checkout = dict(values.get("checkout") or {})

        # Helper: set a value only if it's missing (so we don't overwrite user-typed data)
        def set_if_missing(key, value):
            if value and not checkout.get(key):
                checkout[key] = value

        # Common fields used by website_sale's checkout form
        set_if_missing("name", partner.name)
        set_if_missing("email", partner.email or user.login)
        set_if_missing("phone", partner.phone or partner.mobile)
        set_if_missing("street", partner.street)
        set_if_missing("street2", partner.street2)
        set_if_missing("city", partner.city)
        set_if_missing("zip", partner.zip)
        set_if_missing("country_id", partner.country_id.id if partner.country_id else False)
        set_if_missing("state_id", partner.state_id.id if partner.state_id else False)
        set_if_missing("vat", partner.vat)

        # Push back into values so QWeb inputs can read `checkout[...]`
        values["checkout"] = checkout
        return values
