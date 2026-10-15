"""BUG1281 actual immutable native result vs old literal; no native replay."""
import copy
import json
import unittest
from pg1446_current_cold_stage import W
from pg3262_statement_group_native_rejoin import public_summary, main_source


class ActualNativeSummaryTest(unittest.TestCase):
    @staticmethod
    def actual():
        return json.loads((W / 'pg3262-statement-group-native-qualified-v1/manifest.safe.json').read_text())

    def test_actual3699_not_old3697(self):
        value = self.actual(); before = copy.deepcopy(value); summary = public_summary(value)
        self.assertEqual(3699, summary['tests'])
        self.assertEqual(28, summary['streams'])
        self.assertEqual({'LINE': 603, 'METHOD': 115, 'CLASS': 0, 'BRANCH': 470}, summary['remaining'])
        self.assertEqual(before, value)

    def test_old_foreign_failed_and_missing_never_summary_success(self):
        for key, altered in [('qualifiedFullTests', 3697), ('qualifiedNativeStreams', 27),
                             ('mainClassesIdentical', 1642), ('actualExit', 1)]:
            value = self.actual(); value['result'][key] = altered
            with self.assertRaises(ValueError):
                public_summary(value)
        value = self.actual(); del value['result']['qualifiedFullTests']
        with self.assertRaises(KeyError):
            public_summary(value)
        value = self.actual(); value['actualExit'] = 1
        with self.assertRaises(ValueError):
            public_summary(value)

    def test_complete_main_uses_qualified_result_not_old_literal(self):
        raw = main_source(); compile(raw, '<native transport current summary>', 'exec')
        self.assertIn('safe.update(public_summary(value))', raw)
        self.assertNotIn('safe.update(tests=3697', raw)


if __name__ == '__main__':
    unittest.main()
