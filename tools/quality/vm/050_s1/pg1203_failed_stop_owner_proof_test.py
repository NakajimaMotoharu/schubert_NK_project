import ast
import unittest
from pg1203_failed_stop_owner_proof import payload


class ProofTest(unittest.TestCase):
    def test_fixed_no_signal_scope_generated_closure(self):
        s=payload();ast.parse(s)
        self.assertTrue("cmd.split(b'\\0')[-3:]==[b'Pg1198NativeStop',b'stop',b'']" in s)
        self.assertTrue('all(not v.strip()for v in tasks.values())' in s)
        self.assertTrue('owner==fixed_owner()' in s)
        self.assertFalse('pidfd_send_signal' in s)
        self.assertTrue('actual==completed_current' in s)


if __name__=='__main__':unittest.main()
