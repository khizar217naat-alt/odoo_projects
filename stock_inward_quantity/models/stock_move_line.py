from odoo import models, api
from odoo.osv import expression


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
        Override group by to show net quantity instead of simple sum when grouping by product
        """
        # Check if we're grouping by product and have quantity in fields
        if 'product_id' in groupby and any('quantity' in field for field in fields):

            # First get the standard result
            result = super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

            # For each group, compute the net quantity
            for group in result:
                if group.get('product_id') and 'quantity' in group:
                    product_id = group['product_id'][0]

                    # Create domain for this specific product
                    product_domain = [('product_id', '=', product_id)]
                    if domain:
                        product_domain = expression.AND([product_domain, domain])

                    # Get all move lines for this product with the domain
                    move_lines = self.search(product_domain)

                    # Calculate net quantity
                    net_quantity = 0
                    for move_line in move_lines:
                        location_usage = move_line.location_id.usage
                        location_dest_usage = move_line.location_dest_id.usage

                        # Inward move: from external to internal
                        if (location_usage not in ('internal', 'transit') and
                                location_dest_usage in ('internal', 'transit')):
                            net_quantity += move_line.quantity

                        # Outward move: from internal to external
                        elif (location_usage in ('internal', 'transit') and
                              location_dest_usage not in ('internal', 'transit')):
                            net_quantity -= move_line.quantity
                        # Internal transfers don't affect net quantity

                    # Update the group quantity with net quantity
                    group['quantity'] = net_quantity

            return result
        else:
            # For other groupings, use standard behavior
            return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)