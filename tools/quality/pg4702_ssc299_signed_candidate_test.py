"""Unit fixture only: real selected class bytes, never fabricated whole acceptance."""
import copy
import hashlib
import json
import unittest
from pyflakes.api import checkPath
import pg4702_ssc299_signed_candidate as tool


class CandidateSSC299(unittest.TestCase):
    def fixture(self):
        baseline = json.loads((tool.W / 'pg4428-shared-manager-whole-qualified-v1/manifest.safe.json').read_bytes())['result']
        gate = copy.deepcopy(baseline)
        actual = {}
        for module in tool.prior.MODULES:
            root = tool.W / 'pg4690-entry-termination-selected-v1/source' / ('src/schubert-nk-' + module + '/target/classes')
            actual.update({module + ':' + str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*.class')})
        rows, unchanged = tool.physical_difference(baseline['allPhysicalMainSha256'], actual, actual)
        gate.update(productionSource=tool.SOURCE, tests=3739, suites=549, mainClasses=1646,
                    testClassAliases={}, newCases=[list(v) for v in tool.NEW_CASES],
                    allPhysicalMainSha256=actual, changedClasses=rows, unchangedPhysicalClasses=unchanged)
        gate['modules']['batch']['tests'] += 18
        gate['modules']['batch']['suites'] += 4
        gate['modules']['batch']['mainClasses'] += 2
        return {'actualExit': 0, 'result': gate}, baseline['allPhysicalMainSha256']

    def test_fixed_full_scope_and_actual_selected_physical_bytes_never_relaxed(self):
        fixture, old = self.fixture()
        gate = tool.validate_gate(fixture, tool.SOURCE)
        previous = tool.GATE
        try:
            tool.GATE = gate
            self.assertEqual(1646, tool.verify_delta(tool.grouped(old), tool.grouped(gate['allPhysicalMainSha256'])))
            bad = dict(old); bad[next(iter(bad))] = 'f' * 64
            with self.assertRaises(ValueError): tool.verify_delta(tool.grouped(bad), tool.grouped(gate['allPhysicalMainSha256']))
        finally: tool.GATE = previous
        for key, value in [('tests', 3721), ('suites', 545), ('mainClasses', 1644),
                           ('productionSource', tool.OLD_SOURCE), ('FESFlakyNotRun', False),
                           ('global100', True), ('F03Accepted', True), ('candidateNativePending', False)]:
            bad = copy.deepcopy(fixture); bad['result'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): tool.validate_gate(bad, tool.SOURCE)

    def test_only_current_release_new_paths_and_explicit_order_gap(self):
        raw = tool.main_source()
        for literal in ["'tests': 3739", "'suites': 549", "'mainClasses': 1646", "'addedClasses': 2",
                        "'allSixFormatBeforeAnyPt': False", 'BUG1381/YKT1147',
                        "'0.1.0-PG4432'", "'0.1.0-PG4702'", 'pg4696-ssc299-whole-qualified-v1']:
            self.assertIn(literal, raw)
        self.assertNotIn('pg4428-shared-manager-whole-qualified-v1', raw)
        self.assertEqual(0, checkPath(tool.__file__))
        self.assertEqual(0, checkPath(__file__))


if __name__ == '__main__': unittest.main()
