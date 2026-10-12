"""Actual namespace literals rather than the source substitution alone."""
import unittest
import pg1648_completed_unused_dispatch_v2 as p


class ActualNamespaceTest(unittest.TestCase):
    def test_actual_globals_are_one_current_generation(self):
        ns = p.namespace({'actualExit': 0, 'candidateSource': '2741c4546afad6c1e8b6efbd53dfb58144edf7bb', 'manifestSha256': 'a' * 64})
        self.assertEqual('/home/mini/codex/project1/work/pgpt-runs/PG379/pg1645-completed-unused-tools-v2', str(ns['TARGET']))
        self.assertEqual('/var/lib/pgpt-s1-preservation/pg1645-completed-unused-tools-v2', ns['GUEST'])
        self.assertEqual('/home/ubuntu/pg1646-candidate-input-v1', ns['REMOTE'])
        self.assertEqual('a' * 64, ns['DIGEST'])
        self.assertEqual('9f18ef24f4b236dddcf6c4de228e1c45ffb09c52d9229516a82829bfb6ce3b37', ns['BASELINE_SHA'])
        self.assertIn("base=W/('pg1648-'+action+'-v2')", p.source())
        self.assertIn("W/'pg1648-stage-v2.exit'", p.source())
        for key in ['P', 'W', 'SSH', 'OPTIONS']:
            self.assertEqual(p.prior.previous.__dict__[key], ns[key])
        for bad in [None, {}, {'actualExit': 1, 'candidateSource': ns['SOURCE']}, {'actualExit': 0, 'candidateSource': 'old'}]:
            with self.assertRaises(ValueError):
                p.namespace(bad)


if __name__ == '__main__':
    unittest.main()
