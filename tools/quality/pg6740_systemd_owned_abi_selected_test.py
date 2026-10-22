import unittest
import pg6740_systemd_owned_abi_selected as p
from pg5966_api_sql_selected import source_test_names


class OwnedAbiDefinitionTest(unittest.TestCase):
    def test_exact_independent_two_cases_and_all_six_guards(self):
        cases,counts=p.inventory()
        self.assertEqual((34,9),(sum(counts.values()),len(counts)))
        self.assertEqual(6,len(cases))
        self.assertEqual({'abi001AllOwnedSymbolsDispatchIndependentBoundaryVectors','abi002MissingAndUnknownSymbolsRemainUnavailableWithoutInvocation'},source_test_names(p.ROOT/p.TEST))

    def test_profile_compiles_without_executing_native_or_jobs(self):
        code=p.profile.runner(*p.EXPECTED,{'bootstrap':['bootstrap/LinuxSystemdSession$Native']})
        self.assertIn('len(physical)==1667',code)
        self.assertIn('partial coverage is reported',code)
        self.assertNotIn('done=done and target100',code)


if __name__=='__main__':unittest.main()
