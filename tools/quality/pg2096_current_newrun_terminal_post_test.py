"""Actual metadata namespace, original rows/assets retained after this stop, finite normal marker."""
import unittest
from pg2096_current_newrun_terminal_post import payload,entry,SLOT
from pg2040_fresh_normal_warning_terminal_post import SEALS


class Post(unittest.TestCase):
    def test_actual_whole_source_and_current_only_stop(self):
        raw=payload({n:'a'*64 for n in SEALS})
        for marker in ['pg2090-native-stop-v1','all24UnchangedTwice','allTenUnitsKernelEmpty','allClientAdvisoryFlock0','manager.UnrefUnit(u)','metadata_scope','bus.close()','588342','646556','647598','649480','605603']:
            self.assertTrue(marker in raw,marker)
        self.assertEqual(SLOT,entry().__globals__['SLOT'])


if __name__=='__main__':unittest.main()
