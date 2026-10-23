"""BUG1644/YKT1397: independent current-hash/owner contract, no production PT."""
import unittest

from pg6998_c07_requirement_map import verified_owner


class OwnerMappingTest(unittest.TestCase):
    def test_current_hash_not_historical_hash(self):
        logical = dict(path='public.java',owner='WBS-P018-05',costOwner='WBS-P018-05',sha256='old')
        physical = dict(logical,sha256='new')
        self.assertEqual(('WBS-P018-05','WBS-P018-05'), verified_owner(logical,physical,'new'))
        with self.assertRaises(ValueError):
            verified_owner(logical,physical,'old')
        with self.assertRaises(ValueError):
            verified_owner(logical,dict(physical,owner='WBS-C07'),'new')


if __name__ == '__main__':
    unittest.main()
