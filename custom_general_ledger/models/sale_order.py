from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vendor_id = fields.Many2one(
        'res.partner',
        string="Vendor",
        domain=[('supplier_rank', '>', 0)]  # only vendors
    )

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update({
            'vendor_id': self.vendor_id.id,
            'project_id': self.project_id.id if self.project_id else False,
        })
        return invoice_vals


class AccountMove(models.Model):
    _inherit = 'account.move'

    vendor_id = fields.Many2one(
        'res.partner',
        string="Vendor",
        domain=[('supplier_rank', '>', 0)]  # keep same restriction
    )

    project_id = fields.Many2one(
        'project.project',
        string="Project",
    )
