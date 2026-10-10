"""Independent assertions on actual generated terminal, action and freeze boundaries."""
import unittest
from pg1311_ordinary_publication_sources_v3 import sources
from pg1308_ordinary_publication_sources_v2 import sources as old


class CorrectedPublicationTest(unittest.TestCase):
    def test_actual_terminal_does_not_claim_epoch_writes_zero(self):
        code=sources()['Pg1311OrdinaryPublication.java']
        self.assertNotIn('startsStopsReloadsEpochWrites0',code)
        self.assertEqual(code.count('startsStopsReloads0=true canonicalEpochWrites=1'),2)
        self.assertEqual(code.count('permits.invalidate(old.boot(),fresh,old.activation())'),1)
        self.assertIn('"activate".equals(args[0])',code)
        self.assertIn('"pg1311-approval.part"',code)
        self.assertIn('/pg1311-unused-stage-v1',code)
        self.assertIn('startsStopsReloadsEpochWrites0=true',old()['Pg1308OrdinaryPublication.java'])

    def test_child_namespace_and_fixed_exchange_remain_distinct(self):
        files=sources();child=files['pg1311_native_refs.py']
        self.assertIn("sys.argv[1] == 'activate'",child)
        self.assertIn("'pg1305-current.part'",child)
        self.assertIn('publication_phase',child)
        self.assertNotIn('pg1308',child)
        self.assertIn('pg1304_ordinary_publication_contract.py',files)
        self.assertIn('pg1305_ordinary_exchange_io.py',files)


if __name__=='__main__':unittest.main()
