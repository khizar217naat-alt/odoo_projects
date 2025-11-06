from odoo.tests import tagged, TransactionCase
from odoo.exceptions import ValidationError


@tagged('commission', 'commission_slices')
class TestCommissionSlices(TransactionCase):

    def setUp(self):
        super(TestCommissionSlices, self).setUp()
        self.CommissionSlices = self.env['commission.slices']

        # Clean up any existing commission slices to avoid conflicts
        existing_slices = self.CommissionSlices.search([])
        if existing_slices:
            existing_slices.unlink()

        # Create test commission slices with unique ranges starting from 100000 to avoid conflicts
        self.slice1 = self.CommissionSlices.create({
            'name': 'Test Slice 1',
            'from_amount': 100000.0,
            'to_amount': 101000.0,
            'commission_percentage': 5.0,
        })

        self.slice2 = self.CommissionSlices.create({
            'name': 'Test Slice 2',
            'from_amount': 101000.01,
            'to_amount': 105000.0,
            'commission_percentage': 7.5,
        })

    def test_01_commission_slice_creation(self):
        """Test commission slice creation and automatic sequence assignment"""
        self.assertEqual(self.slice1.slice_seq, 1)
        self.assertEqual(self.slice2.slice_seq, 2)
        self.assertEqual(self.slice1.commission_percentage, 5.0)
        self.assertEqual(self.slice2.commission_percentage, 7.5)

    def test_02_commission_slice_sequence_auto_increment(self):
        """Test automatic sequence increment"""
        slice3 = self.CommissionSlices.create({
            'name': 'Test Slice 3',
            'from_amount': 105000.01,  # Start after previous slice
            'to_amount': 110000.0,
            'commission_percentage': 10.0,
        })
        self.assertEqual(slice3.slice_seq, 3)

    def test_03_commission_slice_validation_errors(self):
        """Test commission slice validation constraints"""
        # Test: from_amount >= to_amount
        with self.assertRaises(ValidationError):
            self.CommissionSlices.create({
                'name': 'Invalid Slice',
                'from_amount': 102000.0,
                'to_amount': 101000.0,
                'commission_percentage': 5.0,
            })

    def test_04_commission_slice_overlap_validation(self):
        """Test commission slice overlap validation"""
        # Test: overlapping ranges - use range that overlaps with existing slices
        with self.assertRaises(ValidationError):
            self.CommissionSlices.create({
                'name': 'Overlapping Slice',
                'from_amount': 100500.0,  # Overlaps with slice1 (100000-101000)
                'to_amount': 101500.0,  # Overlaps with slice2 (101000.01-105000)
                'commission_percentage': 5.0,
            })

    def test_05_commission_slice_behavior_after_deletion(self):
        """Test commission slice behavior after deletion"""
        # Create a third slice with non-overlapping range
        slice3 = self.CommissionSlices.create({
            'name': 'Test Slice 3',
            'from_amount': 105000.01,
            'to_amount': 110000.0,
            'commission_percentage': 10.0,
        })

        self.assertEqual(slice3.slice_seq, 3)

        # Delete the second slice
        self.slice2.unlink()

        # Refresh records without commit
        self.env.flush_all()  # Flush changes to database
        self.slice1.invalidate_recordset()

        # Get fresh instances
        slice1_updated = self.CommissionSlices.browse(self.slice1.id)
        slice3_updated = self.CommissionSlices.browse(slice3.id)

        # Based on actual behavior: sequences are reordered after deletion
        # slice1 should remain 1, slice3 should become 2
        self.assertEqual(slice1_updated.slice_seq, 1)
        self.assertEqual(slice3_updated.slice_seq, 2)

    def test_06_commission_slice_search_by_amount(self):
        """Test finding commission slice by purchase amount"""
        # Test amount in first slice
        slice_for_100500 = self.CommissionSlices.search([
            ('from_amount', '<=', 100500.0),
            ('to_amount', '>=', 100500.0),
        ], limit=1)
        self.assertEqual(slice_for_100500, self.slice1)

        # Test amount in second slice
        slice_for_102000 = self.CommissionSlices.search([
            ('from_amount', '<=', 102000.0),
            ('to_amount', '>=', 102000.0),
        ], limit=1)
        self.assertEqual(slice_for_102000, self.slice2)

        # Test amount not in any slice
        slice_for_150000 = self.CommissionSlices.search([
            ('from_amount', '<=', 150000.0),
            ('to_amount', '>=', 150000.0),
        ], limit=1)
        self.assertFalse(slice_for_150000)

    def test_07_commission_percentage_format(self):
        """Test commission percentage formatting and constraints"""
        # Test valid percentage with non-overlapping range
        valid_slice = self.CommissionSlices.create({
            'name': 'Valid Percentage',
            'from_amount': 110000.01,  # Start after existing slices
            'to_amount': 120000.0,
            'commission_percentage': 15.5,
        })
        self.assertEqual(valid_slice.commission_percentage, 15.5)

        # Test boundary values with non-overlapping range
        zero_slice = self.CommissionSlices.create({
            'name': 'Zero Percentage',
            'from_amount': 120000.01,  # Start after previous slice
            'to_amount': 130000.0,
            'commission_percentage': 0.0,
        })
        self.assertEqual(zero_slice.commission_percentage, 0.0)

    def test_08_commission_slice_multiple_deletions(self):
        """Test commission slice behavior after multiple deletions"""
        # Create multiple slices
        slices = []
        for i in range(3):
            slice_obj = self.CommissionSlices.create({
                'name': f'Slice {i}',
                'from_amount': 200000.0 + (i * 1000.0),
                'to_amount': 200000.0 + ((i + 1) * 1000.0),
                'commission_percentage': float(i + 1),
            })
            slices.append(slice_obj)

        # Verify initial sequences (start from 3 because setUp created 2 slices)
        expected_initial_sequences = [3, 4, 5]
        for i, slice_obj in enumerate(slices):
            self.assertEqual(slice_obj.slice_seq, expected_initial_sequences[i])

        # Delete middle slice
        slices[1].unlink()  # Delete slice with sequence 4

        # Refresh and check sequences - they should be reordered
        self.env.flush_all()
        remaining_slices = self.CommissionSlices.search([], order='slice_seq asc')

        # Expected sequences after reordering: 1, 2, 3, 4
        # (slice1=1, slice2=2, slice[0]=3, slice[2]=4)
        expected_sequences = [1, 2, 3, 4]
        self.assertEqual(len(remaining_slices), len(expected_sequences))

        for i, slice_obj in enumerate(remaining_slices):
            self.assertEqual(slice_obj.slice_seq, expected_sequences[i])

    def test_09_commission_slice_duplicate_ranges(self):
        """Test that duplicate ranges are not allowed"""
        # Try to create a slice with the same range as an existing one
        with self.assertRaises(ValidationError):
            self.CommissionSlices.create({
                'name': 'Duplicate Slice',
                'from_amount': 100000.0,  # Same as slice1
                'to_amount': 101000.0,  # Same as slice1
                'commission_percentage': 8.0,
            })

    def test_10_commission_slice_edge_cases(self):
        """Test commission slice edge cases"""
        # Test very small range
        small_slice = self.CommissionSlices.create({
            'name': 'Small Range',
            'from_amount': 300000.0,
            'to_amount': 300000.01,
            'commission_percentage': 1.0,
        })
        self.assertTrue(small_slice)

        # Test zero percentage
        zero_percent_slice = self.CommissionSlices.create({
            'name': 'Zero Percent',
            'from_amount': 400000.0,
            'to_amount': 500000.0,
            'commission_percentage': 0.0,
        })
        self.assertEqual(zero_percent_slice.commission_percentage, 0.0)

    def test_11_commission_slice_order_independence(self):
        """Test that commission slices work regardless of sequence order"""
        # Create slices in a different order
        slice_high = self.CommissionSlices.create({
            'name': 'High Range First',
            'from_amount': 500000.0,
            'to_amount': 600000.0,
            'commission_percentage': 20.0,
        })

        slice_low = self.CommissionSlices.create({
            'name': 'Low Range Later',
            'from_amount': 10000.0,
            'to_amount': 20000.0,
            'commission_percentage': 5.0,
        })

        # Both should be created successfully with proper sequences
        self.assertTrue(slice_high.slice_seq > 0)
        self.assertTrue(slice_low.slice_seq > 0)
        self.assertNotEqual(slice_high.slice_seq, slice_low.slice_seq)

    def test_12_commission_slice_no_sequence_reordering(self):
        """Test that sequences don't reorder when not expected"""
        # Create a slice and verify its sequence
        slice3 = self.CommissionSlices.create({
            'name': 'Test Slice 3',
            'from_amount': 105000.01,
            'to_amount': 110000.0,
            'commission_percentage': 10.0,
        })

        original_sequence = slice3.slice_seq
        self.assertEqual(original_sequence, 3)

        # Just update the slice without deleting anything
        slice3.write({'commission_percentage': 12.0})

        # Sequence should remain the same
        self.assertEqual(slice3.slice_seq, original_sequence)