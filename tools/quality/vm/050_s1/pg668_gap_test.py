"""PG668-C001 no stale qualification/byte paths or source substitution."""
import ast
import unittest
from pg668_gap import code


class Test(unittest.TestCase):
    def test_all23_qualified_only(self):
        raw=code('a'*64);ast.parse(raw)
        for s in('pg666-current-seventeen-native-v1','pg668-current-native-gap-v1','assert len(data)==23',"record['bootstrap']['sha256']",'qualificationManifests','class','moduleCounters'):
            self.assertIn(s,raw)
        for s in('pg658-same-source-sixteen-native-v1','pg660-current-native-gap-v1','assert len(data)==22','23b14a44','pg599-candidate'):
            self.assertNotIn(s,raw)


if __name__=='__main__':unittest.main()
