import unittest
import pg5898_serial_identity5_review as target


class SerialFiveSourceBindingTest(unittest.TestCase):
    def test_old_source_bound_in_its_own_function_globals_and_five_pending(self):
        self.assertEqual(target.OLD_SOURCE,target.prior_index_function().__globals__['OLD'])
        self.assertNotEqual(target.previous.OLD,target.prior_index_function().__globals__['OLD'])
        raw=target.reader_source();self.assertIn('len(held)!=5',raw);self.assertIn('len(decisions)!=5',raw)
        self.assertIn('PG5876-current-static3971-v1',raw);self.assertIn('pg5896-serial-reference-facts-v1',raw)
        self.assertIn('currentWholeCaseRefs=[]',raw)


if __name__=='__main__':unittest.main()
