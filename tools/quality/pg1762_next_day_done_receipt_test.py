"""Actual source binds new captured generation and retains immutable parent budget."""
import unittest
from pg1762_next_day_done_receipt import payload,EXPECTED,OLD

class Done(unittest.TestCase):
    def test_actual_new_fields_old_claims_absent_and_original_time_budget(self):
        raw=payload()
        for k in ('invocation','job','run','cutoff','activation'):
            self.assertIn(EXPECTED[k],raw);self.assertNotIn(OLD[k],raw)
        self.assertIn(str(EXPECTED['start']),raw)
        self.assertIn('1800000000',raw)
        self.assertIn('pg1762-next-day-done-receipt-v1',raw)
        self.assertNotIn('pidfd_send_signal',raw)

if __name__=='__main__':unittest.main()
