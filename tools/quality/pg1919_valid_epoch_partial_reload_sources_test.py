"""Independent selected INVALID and record's hash envelope remain separate vectors."""
import unittest
from pg1919_valid_epoch_partial_reload_sources import sources


class Epoch(unittest.TestCase):
    def test_actual_fixture_factory_and_invalid_original_are_not_both_swapped(self):
        s=sources();j=s['Pg1919OriginalTupleTest.java'];real=s['Pg1919PartialReload.java']
        self.assertIn('state==StartupPermitRecords.State.ISSUED?Optional.of("a".repeat(64)):Optional.empty()',j)
        self.assertNotIn('state==StartupPermitRecords.State.INVALID?Optional.of',j)
        self.assertIn('var e=epoch(StartupPermitRecords.State.INVALID,BOOT,activation)',j)
        self.assertIn('rejected(epoch(StartupPermitRecords.State.ISSUED,BOOT,activation),d)',j)
        self.assertIn('epoch.state()==StartupPermitRecords.State.INVALID',real)
        self.assertIn('if(checks!=18)',j)
        self.assertIn('PG1919_INPUT_CLOSURE_READY\\n',real)


if __name__=='__main__':unittest.main()
