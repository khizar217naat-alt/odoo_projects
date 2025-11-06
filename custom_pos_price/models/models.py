from odoo import models, api, _, fields
from odoo.exceptions import UserError

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.model
    def get_existing_lots(self, company_id, product_id):
        # Call super if you want original behavior first
        # original_lots = super().get_existing_lots(company_id, product_id)

        self.check_access('read')
        pos_config = self.env['pos.config'].browse(self._context.get('config_id'))
        if not pos_config:
            raise UserError(_('No PoS configuration found'))

        src_loc = pos_config.picking_type_id.default_location_src_id

        domain = [
            '|',
            ('company_id', '=', False),
            ('company_id', '=', company_id),
            ('product_id', '=', product_id),
            ('location_id', 'in', src_loc.child_internal_location_ids.ids),
            ('quantity', '>', 0),
            ('lot_id', '!=', False),
        ]

        groups = self.sudo().env['stock.quant']._read_group(
            domain=domain,
            groupby=['lot_id'],
            aggregates=['quantity:sum']
        )

        result = []
        for lot_recordset, total_quantity in groups:
            if lot_recordset:
                result.append({
                    'id': lot_recordset.id,
                    'name': lot_recordset.name,
                    'product_qty': total_quantity,
                    'cost_price': lot_recordset.my_price
                })

        # You can also modify or add extra logic here if needed
        return result


class StockLot(models.Model):
    _inherit = "stock.lot"

    my_price = fields.Float(string="My Price", help="Custom POS Sale Price for this lot/serial")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    serial = fields.Many2one(
        "stock.lot",
        string="Serial",
        domain="[('product_id', '=', product_id)]",
    )

    @api.onchange("product_id")
    def _onchange_product_id_tracking(self):
        """When product changes:
        - If tracking is 'lot', propose lots for this product
        - Otherwise clear the selected serial
        """
        domain = []
        if self.product_id and self.product_id.tracking == "lot":
            domain = [('product_id', '=', self.product_id.id)]
        else:
            self.serial = False
        return {"domain": {"serial": domain}}

    @api.onchange("serial")
    def _onchange_serial_set_price(self):
        """If product is lot-tracked and a serial is selected, set price from serial.my_price."""
        if not self.serial or not self.product_id:
            return
        # Only apply for lot-tracked products and matching product on the lot
        if self.product_id.tracking == "lot" and (not self.serial.product_id or self.serial.product_id == self.product_id):
            # Assume custom field my_price exists on stock.lot
            self.price_unit = self.serial.my_price or 0.0