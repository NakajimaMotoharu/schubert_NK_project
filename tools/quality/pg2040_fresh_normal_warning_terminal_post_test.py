"""Actual complete marker is independent literal; metadata refs/row/null/lock0 closure retained."""
import unittest
from pg2040_fresh_normal_warning_terminal_post import payload,SEALS


class Post(unittest.TestCase):
    def test_actual_normal_marker_and_whole_post(self):
        raw=payload({name:'a'*64 for name in SEALS})
        for wanted in ['genuineParentDone=true','normalUnit0or10=true','pg2030-native-stop-v1','pg2030-fresh-normal-warning-owned-stop-tools-v1','all24UnchangedTwice','allTenUnitsKernelEmpty','allClientAdvisoryFlock0','manager.UnrefUnit(u)','bus.close()']:
            self.assertTrue(wanted in raw,wanted)
        for forbidden in ['managerFailureRetained=true','pg1833-native-stop-v1','pg1833-warning-owned-stop-tools-v1']:
            self.assertTrue(forbidden not in raw,'no old authority '+forbidden)


if __name__=='__main__':unittest.main()
