# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    # Add discount_amount field to store absolute discount amount
    discount_amount = fields.Float(
        string='Discount Amount',
        digits='Product Price',
        default=0.0,
        help="Absolute discount amount in currency"
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Override to include discount_amount in POS data loading"""
        fields = super()._load_pos_data_fields(config_id)
        if 'discount_amount' not in fields:
            fields.append('discount_amount')
        return fields

    @api.model
    def _order_line_fields(self, line, session_id=None):
        """Override to include discount_amount when processing order lines"""
        result = super()._order_line_fields(line, session_id)
        if line and 'discount_amount' in line:
            result[2]['discount_amount'] = line['discount_amount']
        return result