"""Exact completed named-role transport/server; no guest operation."""
import unittest
import pg2916_failed_pair_boundary_selected as p


class FailedPairInputs(unittest.TestCase):
    def test_complete_graph_and_positive_named_test_count(self):
        raw=p.server();body=p.transport_body()
        for s in ['source-full-PG2798','BackupFailureSnapshotTest','SelectedClassContractLauncher',"'name':'PG2916'",'cfdb2916002EveryNullColumnAndMissingResourceIsBounded','require(not mainclasses)']:
            self.assertIn(s,raw)
        self.assertNotIn('mdb2792001',raw)
        self.assertIn('ROOT/TEST',body)
        self.assertNotIn('ROOT/FILES[1]',body)
        self.assertEqual(6,(p.prior.prior.ROOT/p.TEST).read_text().count('@Test\n'))


if __name__=='__main__':unittest.main()
