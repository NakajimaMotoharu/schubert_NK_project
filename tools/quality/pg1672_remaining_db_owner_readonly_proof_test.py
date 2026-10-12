"""Independent sole-owner full/typed99/no-signal and old dispatch refusal tests."""
import copy
import unittest
from pyflakes.api import check
import pg1672_remaining_db_owner_readonly_proof as p
from pg1673_sole_owner_contract import fresh_sole_parent
from pg1665_unused_pair_contract_test import fixture


class RemainingOwnerTest(unittest.TestCase):
    def test_exact_full_readonly_and_old_signal_refusal(self):
        raw = p.payload()
        self.assertEqual(0, check(raw, '<sole99 DB owner readonly>'))
        self.assertTrue(p.qualify_no_parent_signal())
        for text in ["require(not children)", "len(a['fds'])==99", "=={'100','101'}", "peer==same_peer()==old_pair['peer']", 'fresh_sole_parent(expected_actor']:
            self.assertIn(text, raw)
        for text in ['pidfd_send_signal', 'pg_terminate_backend', 'os.kill(']:
            self.assertNotIn(text, raw)

    def test_all99_guard_and_only_two_chrono(self):
        old = fixture()
        del old['fds']['17']
        del old['fds']['18']
        current = copy.deepcopy(old)
        for n in ['29', '32']:current['fds'][n]['metadata'][7:] = [21, 22]
        self.assertTrue(fresh_sole_parent(old, current, 22))
        for name in old['fds']:
            for index in range(9):
                bad = copy.deepcopy(old)
                bad['fds'][name]['metadata'][index] += 1
                with self.assertRaises(ValueError): fresh_sole_parent(old, bad, 22)
        for bad in [None, fixture(), {}, True]:
            with self.assertRaises(ValueError): fresh_sole_parent(old, bad, 22)


if __name__ == '__main__':
    unittest.main()
