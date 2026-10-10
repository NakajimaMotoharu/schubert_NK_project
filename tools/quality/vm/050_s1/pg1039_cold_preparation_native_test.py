import ast
import unittest
from pg1039_cold_preparation_native import source


class Transport(unittest.TestCase):
    def test_frozen_current_profile_begin_and_only_new_slots(self):
        raw=source();ast.parse(raw)
        self.assertTrue("('stage','prepare')"in raw)
        self.assertTrue('pg1038-cold-preparation-frozen-v1.safe.json'in raw)
        self.assertTrue('Pg1037ColdOwnedPreparation '+"'+action"in raw)
        self.assertTrue("'operatorSource':begin_record['operatorSource']"in raw)
        self.assertTrue("'fullColdPreparationAccepted':action=='prepare'and code==0"in raw)
        for old in ('pg1025-','pg1023-','Pg1023ColdOwnedReadback','pg1035-cold-owned-handoff-v1'):
            self.assertFalse(old in raw)


if __name__=='__main__':unittest.main()
