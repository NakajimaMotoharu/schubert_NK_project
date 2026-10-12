"""Exact same frozen tool paths and normal-only prepare-ro closed CLI."""
import ast
import inspect
import unittest
from pyflakes.api import check
import pg1688_completed_candidate_ro_dispatch as p


class RoDispatcherTest(unittest.TestCase):
    def test_frozen_paths_and_no_archive_placement(self):
        raw=inspect.getsource(p)
        self.assertEqual(0,check(raw,p.__file__))
        self.assertEqual('/var/lib/pgpt-s1-preservation/pg1686-completed-candidate-ro-tools-v1',p.GUEST)
        self.assertIn('/home/ubuntu/pg1688-fixed-stage-v1/',p.STAGE)
        self.assertIn('pg1686-completed-candidate-ro-tools-v1.tar',p.STAGE)
        self.assertIn("CLASS+' prepare-ro'",raw)
        self.assertIn('management_gate(',raw)
        for x in ['pg1683-release-v4.tar','pg1661','systemctl start','pg_terminate_backend','freezeCandidate']:self.assertNotIn(x,raw)
        ast.parse(p.STAGE)


if __name__=='__main__':unittest.main()
