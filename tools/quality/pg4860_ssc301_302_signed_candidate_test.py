import copy
import json
import unittest
from pyflakes.api import checkPath
import pg4860_ssc301_302_signed_candidate as role


class Candidate(unittest.TestCase):
    def test_actual_whole_identity_and_exact_inventory(self):
        outer = json.loads((role.W/'pg4846-ssc301-302-whole-qualified-v1/manifest.safe.json').read_bytes())
        gate = role.validate_gate(outer, role.SOURCE)
        self.assertTrue(role.qualification_matches(outer))
        old = json.loads((role.W/'pg4696-ssc299-whole-qualified-v1/manifest.safe.json').read_bytes())['result']
        previous = role.GATE
        try:
            role.GATE = gate
            self.assertEqual(1647, role.verify_delta(role.grouped(old['allPhysicalMainSha256']), role.grouped(gate['allPhysicalMainSha256'])))
            bad = dict(gate['allPhysicalMainSha256']); bad[next(iter(bad))] = 'f'*64
            with self.assertRaises(ValueError): role.verify_delta(role.grouped(old['allPhysicalMainSha256']), role.grouped(bad))
        finally: role.GATE = previous
        for key, value in [('tests',3739),('suites',549),('mainClasses',1646),('allSixFormatBeforeAnyPt',False),('productionSource',role.OLD_SOURCE),('formalAccepted',True),('FESFlakyNotRun',False),('candidateNativePending',False)]:
            bad = copy.deepcopy(outer); bad['result'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): role.validate_gate(bad,role.SOURCE)

    def test_candidate_is_new_host_only_not_retrospective_format_repair(self):
        raw = role.main_source()
        for literal in ["'tests': 3761", "'suites': 551", "'mainClasses': 1647", "'addedClasses': 1", "'allSixFormatBeforeAnyPt': True", "'formatOrderIssue': None", "'0.1.0-PG4702'", "'0.1.0-PG4860'", "{'VERSION', 'api/api.jar', 'operations/batch.jar'} <= changed", 'pg4846-ssc301-302-whole-qualified-v1']:
            self.assertIn(literal,raw)
        self.assertNotIn('BUG1381', raw)
        self.assertEqual(0, checkPath(role.__file__)); self.assertEqual(0, checkPath(__file__))


if __name__ == '__main__': unittest.main()
