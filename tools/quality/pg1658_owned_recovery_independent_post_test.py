"""Inspect actual full independent post and exact six private handoff files."""
import unittest
from pyflakes.api import check
import pg1658_owned_recovery_independent_post as p


class IndependentPostTest(unittest.TestCase):
    def test_actual_complete_post_not_prior_success(self):
        raw = p.payload()
        self.assertEqual(0, check(raw, '<actual recovery full post>'))
        for text in ['not pathlib.Path(\'/proc/289328\').exists()', 'fresh-complete.private', '289328.term-once.private', "reservation['actor']==fresh['actor']", 'oldCloseUnknown', 'all24And32And187Unchanged', "==after['runtime']", 'len(rows)==24', 'pg1658-owned-recovery-independent-post-v1']:
            self.assertIn(text, raw)
        self.assertNotIn('pidfd_send_signal', raw)
        self.assertNotIn('systemctl start', raw)
        self.assertNotIn('systemctl stop', raw)


if __name__ == '__main__':
    unittest.main()
