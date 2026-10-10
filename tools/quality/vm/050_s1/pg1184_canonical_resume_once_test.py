import ast
import unittest
from pg1184_canonical_resume_once import payload


class CanonicalOnceTest(unittest.TestCase):
    def test_same_active_fullproof_observer_and_durable_once(self):
        s = payload();ast.parse(s)
        self.assertEqual(s.count("['/usr/bin/systemctl','start','--no-block','schubert-nk-morning-controller.service']"), 1)
        self.assertLess(s.index("persist('external-start-guard.private.json'"), s.index('result=subprocess.run('))
        self.assertTrue('watch();require(observed==post())' in s)
        for part in ['424273', '5109843', '5869c4d00b38e1b32631fdf171ccd920ef6e3b595db61144c15f4e762a8a510b', "'sameActivation':ACT", "'originalBudgetSeconds':1800", 'manager.UnrefUnit(u)', 'repeatForbidden']:
            self.assertTrue(part in s, part)
        for forbidden in ['daemon-reload', 'pidfd_send_signal', "['/usr/bin/systemctl','stop'", 'runtime.owned_prepare(']:
            self.assertFalse(forbidden in s, forbidden)


if __name__ == '__main__':unittest.main()
