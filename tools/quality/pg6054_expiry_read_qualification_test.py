import copy
import unittest
import pg6054_expiry_read_qualification as t


class OriginalVerdictNoPromotionTest(unittest.TestCase):
    def test_terminal_source_exact_xml_and_six_static_are_separate_required_facts(self):
        expected = {'public.fixture': {'one'}}
        begin = dict(source=t.SOURCE, expectedTests=148, expected={'public.fixture': ['one']})
        result = dict(source=t.SOURCE, actualExit=0, mavenActualExit=0, phaseExits=[0, 0],
            exactInventory=True, sourceFixed=True, selectedQualified=True, failedOrSkipped=[],
            tests=148, suites=16, staticIssues={k: 0 for k in t.MODULES})
        t.actual_original(result, begin, expected)
        for key, value in (('source', 'old-source'), ('actualExit', 1), ('mavenActualExit', 1),
            ('phaseExits', [0, 1]), ('tests', 147), ('suites', 15), ('exactInventory', False),
            ('sourceFixed', False), ('failedOrSkipped', ['not-pass']),
            ('staticIssues', {k: 0 for k in t.MODULES[:-1]})):
            changed = copy.deepcopy(result); changed[key] = value
            with self.assertRaises(ValueError):
                t.actual_original(changed, begin, expected)
        with self.assertRaises(ValueError):
            t.actual_original(result, dict(begin, source='other-source'), expected)
        with self.assertRaises(ValueError):
            t.actual_original(result, begin, {'public.fixture': {'another'}})


if __name__ == '__main__':
    unittest.main()
