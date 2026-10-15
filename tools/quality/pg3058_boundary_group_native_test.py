"""Independent count/source/member rejection and complete no-VM payload test."""
import ast
import unittest
from pyflakes.api import check
from pg3058_boundary_group_native_rejoin import SOURCE, build_payload


class Qualification(unittest.TestCase):
    def test_wrong_scope_counts_source_and_failure_cannot_enter(self):
        full = {'productionSource': SOURCE, 'tests': 3691, 'suites': 542, 'mainClasses': 1643, 'FESFlakyNotRun': 0, 'staticSixModules': 0}
        for key, bad in [('productionSource', 'foreign'), ('tests', 3685), ('suites', 541), ('mainClasses', 1642), ('FESFlakyNotRun', 1), ('staticSixModules', 1)]:
            with self.assertRaises(ValueError):
                build_payload({**full, key: bad})
        raw = build_payload(full)
        ast.parse(raw)
        self.assertEqual(0, check(raw, '<complete new3691 native server>'))
        for required in ["full=FULL", 'PG3054-six-v1', 'main_count==1643 and resource_count==79', 'len(streams)==18', "len({s['sessionIdSha256']for s in sessions})==18", 'PG2934-native-v1', 'PG3030-native-v1', 'for n,h in v[\'files\'].items():require(sha(root/n)==h)']:
            self.assertIn(required, raw)
        for forbidden in ['PG3026-six-v1', 'systemctl', 'daemon-reload', '04207efc', '0fd734']:
            self.assertNotIn(forbidden, raw)


if __name__ == '__main__':
    unittest.main()
