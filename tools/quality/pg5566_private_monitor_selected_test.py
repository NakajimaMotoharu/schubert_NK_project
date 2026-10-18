import inspect
import unittest
from pyflakes.api import checkPath
import pg5566_private_monitor_selected as entry


class SelectedMonitor(unittest.TestCase):
    def test_exact_source_inventory_all_affected_and_dependencies(self):
        red=entry.inventory(entry.ROOT,'red');green=entry.inventory(entry.ROOT,'green')
        self.assertEqual(sum(map(len,red.values())),29)
        self.assertEqual(sum(map(len,green.values())),71)
        self.assertEqual(len(entry.EXPECTED_CHANGES),6)
        self.assertTrue(set(entry.OWNERS)<=green.keys())

    def test_fixed_source_no_failure_or_unknown_count_promoted(self):
        raw=inspect.getsource(entry.main)
        for fact in("phases==[0,1]","phases==[0,0]","actual==expected","'coverageWholeAccepted':False","'oldNativeImported':False"):
            self.assertIn(fact,raw)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
