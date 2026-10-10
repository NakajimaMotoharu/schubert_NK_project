import ast
import unittest
from pg1182_canonical_runtime_post import payload


class CanonicalPostTest(unittest.TestCase):
    def test_full_independent_three_read_join_no_config_operations(self):
        s = payload();ast.parse(s)
        for part in ['require(v==prior)', "expected['configuration']", "expected['runtime']", 'canonical_configuration(', '3e1e7d324d95c493ba24429f7cd1abc81c996566b99ac0ce40f46b61236d3325', 'b341bb8f210cab1e5e688b20e445c477ea81410efdc73c521d151072aaf61073', 'observed==post()', 'resource_zero()']:
            self.assertTrue(part in s, part)
        for forbidden in ['daemon-reload', 'pidfd_send_signal', 'systemctl start', 'systemctl stop']:
            self.assertFalse(forbidden in s, forbidden)


if __name__ == '__main__':unittest.main()
