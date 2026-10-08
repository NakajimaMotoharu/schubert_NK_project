"""Qualified16/host6/hash/missed counters XML binding only."""
import unittest
from pg660_native_gap import code


class Binding(unittest.TestCase):
    def test_only_qualified_current_two_manifests_and_exact_counters(self):
        v=code('1'*64);compile(v,'<qualified16 XML>','exec')
        for x in ('pg658-same-source-sixteen-native-v1','pg660-current-native-gap-v1','pg644-current-eight-native-v1','pg657-normal-eight-native-v1',"record['qualificationManifests'][name]",'len(data)==22', 'record[\'moduleCounters\']', 'NativeCoverageXml471', 'sourceOrClassExclusions'):
            self.assertIn(x,v)
        for x in ('pg614-current-eight-native-v1','pg599-candidate','23b14a44'):
            self.assertNotIn(x,v)


if __name__=='__main__':unittest.main()
