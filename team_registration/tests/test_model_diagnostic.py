from odoo.tests import tagged, TransactionCase
import logging

_logger = logging.getLogger(__name__)


@tagged('diagnostic', 'post_install', '-at_install')
class TestModelDiagnostic(TransactionCase):
    """Diagnostic test to check model structure"""

    def test_user_commission_track_structure(self):
        """Check the structure of user.commission.track model"""
        model = self.env['user.commission.track']

        _logger.info("=== User Commission Track Model Diagnostic ===")

        # Check status field
        status_field = model._fields.get('status')
        if status_field:
            _logger.info("Status field type: %s", type(status_field).__name__)
            if hasattr(status_field, 'selection'):
                _logger.info("Status selections: %s", status_field.selection)
            else:
                _logger.info("Status field has no selection attribute")
        else:
            _logger.info("Status field not found in model")

        # Check all fields
        _logger.info("All fields in model:")
        for field_name, field in model._fields.items():
            _logger.info("  %s: %s", field_name, type(field).__name__)

        # Check available methods
        _logger.info("Available methods:")
        method_list = [method for method in dir(model) if
                       not method.startswith('_') and callable(getattr(model, method))]
        for method in sorted(method_list):
            _logger.info("  %s", method)