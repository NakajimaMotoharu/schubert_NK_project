import ast
import copy
import unittest
from pyflakes.api import checkPath
import pg6470_web_owned_component_selected as profile
import pg6054_expiry_read_qualification as reader


class CompileFirst(unittest.TestCase):
    def test_three_exact_phases_skip_only_the_compile_lifecycle(self):
        raw = profile.prior.prior.prior.runner_source(27, 11, 2)
        prepared = profile.compile_first(raw)
        self.assertEqual(1, prepared.count("base+['-DskipTests','test-compile']"))
        self.assertEqual(1, prepared.count("base+['-Dtest='"))
        self.assertIn('exits==[0,0,0]', prepared)
        ast.parse(prepared)
        with self.assertRaises(ValueError): profile.compile_first(prepared)
        with self.assertRaises(ValueError): profile.compile_first(raw.replace("'spotless:check'", "'unknown'"))

    def test_reader_phase_count_is_not_a_failure_waiver(self):
        expected = {'public.fixture': {'one'}}
        begin = dict(source=reader.SOURCE, expectedTests=27, expected={'public.fixture': ['one']})
        result = dict(source=reader.SOURCE, actualExit=0, mavenActualExit=0, phaseExits=[0, 0, 0],
            exactInventory=True, sourceFixed=True, selectedQualified=True, failedOrSkipped=[],
            tests=27, suites=11, staticIssues={k: 0 for k in reader.MODULES})
        reader.actual_original(result, begin, expected, expected_counts=(27,11), expected_phase_exits=(0,0,0))
        with self.assertRaises(ValueError): reader.actual_original(result, begin, expected, expected_counts=(27,11))
        for phases in ([0,0], [0,1,0], [0,0,1], [0,0,0,0], []):
            changed = copy.deepcopy(result); changed['phaseExits'] = phases
            with self.assertRaises(ValueError): reader.actual_original(changed, begin, expected, expected_counts=(27,11), expected_phase_exits=(0,0,0))
        with self.assertRaises(ValueError): reader.actual_original(result, begin, expected, expected_counts=(27,11), expected_phase_exits=(0,1,0))

    def test_inventory_and_tools_lint(self):
        _, counts = profile.inventory()
        self.assertEqual((27,11), (sum(counts.values()),len(counts)))
        for name in ('pg6470_web_owned_component_selected.py','pg6486_web_owned_component_v3.py','pg6488_web_owned_component_qualification_v3.py','pg6484_web_owned_runtime_order.py'):
            self.assertEqual(0,checkPath(str(profile.ROOT/'tools/quality'/name)))


if __name__ == '__main__': unittest.main()
