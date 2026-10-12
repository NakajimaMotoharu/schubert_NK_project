"""Actual namespace and positive-only publication action/transition fixture joins."""
import unittest
import pg1695_completed_publication_dispatch as p


class PublicationDispatcherTest(unittest.TestCase):
    def test_exact_frozen_input_not_output_and_real_namespace(self):
        raw=p.source()
        self.assertIn('pg1693-frozen-v1.safe.json',raw)
        self.assertIn('pg1690-completed-candidate-ro-post-v1',raw)
        self.assertIn("(['stage'],['activate'])",raw)
        self.assertIn("'Pg1691TransitionTest',CLASS+' activate'",raw)
        self.assertIn("'currentApprovalEpochChanged':action=='activate'",raw)
        self.assertEqual('/var/lib/pgpt-s1-preservation/pg1691-completed-publication-tools-v1',p.GUEST)
        self.assertIn('/home/ubuntu/pg1695-fixed-stage-v1/',p.STAGE)
        for old in ['pg1688-','prepare-ro','systemctl start','pg_terminate_backend','SOURCE=']:self.assertNotIn(old,raw)


if __name__=='__main__':unittest.main()
