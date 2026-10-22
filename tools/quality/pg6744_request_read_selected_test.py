import unittest
import pg6744_request_read_selected as p
from pg5966_api_sql_selected import source_test_names


class OrdinaryRequestDefinitionTest(unittest.TestCase):
    def test_exact_three_cases_related_domains_and_six_guards(self):
        cases,counts=p.inventory()
        self.assertEqual((47,11),(sum(counts.values()),len(counts)));self.assertEqual(6,len(cases))
        self.assertEqual({'breqRead001UnavailableIsNotMissingAndNeverPublishes','breqRead002SecondValidRecordMismatchNeverRetires','breqRead003FinalDirectoryChangeNeverRetires'},source_test_names(p.ROOT/p.TEST))

    def test_finite_definition_preserves_physical_and_partial_coverage_guards(self):
        raw=p.profile.runner(*p.EXPECTED,{'batch':['batch/file/BackupWorkerRequestFiles'],'bootstrap':['bootstrap/LinuxSystemdSession$Native']})
        self.assertIn('len(physical)==1667',raw);self.assertIn('partial coverage is reported',raw)
        self.assertNotIn('done=done and target100',raw)


if __name__=='__main__':unittest.main()
