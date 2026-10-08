"""PG673-C001 fixed counts/source/module qualification, no cumulative source imports."""
import ast
import unittest
from pg673_collect_full import source


class Test(unittest.TestCase):
    def test_entry_source_qualification_boundaries(self):
        raw=source();ast.parse(raw)
        for s in('pg672-entry-six-host-v1','pg670-entry-component-v1','fec725f2f89945be5c88d5ef98a8446e155e7d701748a118191cdd2c8211f95b',
                 '3477, 277, None','suites == 514 and total_classes == 1608',"selected_module = 'api'",'allMainBytesEqualSelectedCandidate',"'oldNativeStreamsNotImported': True"):
            self.assertIn(s,raw)
        self.assertNotIn('pg628-retention-factory-component-v1',raw)
        self.assertNotIn('e83d2c34652b8c2bea5c1b9c02f00e9b757b88b5de6b1fb45e79b615ec003b57',raw)


if __name__=='__main__':unittest.main()
