from odoo import http
from odoo.http import request
import json


class AccountReportController(http.Controller):

    @http.route('/account_reports/purchase_order_filter', type='json', auth='user')
    def get_po_filtered_data(self, po_id=None, **kwargs):
        """
        Handle PO filtering in account reports
        """
        try:
            # Get the base report data first
            report_data = request.env['account.report'].get_report_data(**kwargs)

            # Apply PO filter if provided
            if po_id:
                po_line = request.env['analytic.po.line'].browse(int(po_id))
                if po_line.exists():
                    # Filter move lines by the selected PO
                    filtered_lines = request.env['account.move.line'].search([
                        ('analytic_po_line_id', '=', po_id)
                    ])

                    # Apply your filtering logic here based on your report structure
                    # This is a simplified example - adjust based on your actual report structure
                    if 'lines' in report_data:
                        report_data['lines'] = [
                            line for line in report_data['lines']
                            if line.get('analytic_po_line_id') == int(po_id)
                        ]

            return report_data
        except Exception as e:
            return {'error': str(e)}