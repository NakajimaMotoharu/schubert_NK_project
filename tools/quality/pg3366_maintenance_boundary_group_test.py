"""Pure guard/selection checks; no Production PT or coverage credit."""
import ast
import unittest
import xml.etree.ElementTree as ET

import pg3366_maintenance_boundary_group as target


class RelatedGuards(unittest.TestCase):
    def test_every_selected_source_exists_and_counts_match(self):
        self.assertEqual(6, len(target.CLASSES))
        self.assertEqual(54, sum(sum(v.values()) for v in target.CLASSES.values()))
        self.assertEqual(7, sum(len(v) for v in target.CLASSES.values()))
        for module, values in target.CLASSES.items():
            for name, count in values.items():
                p = target.ROOT / ('src/schubert-nk-' + module + '/src/test/java/' + name.replace('.', '/') + '.java')
                self.assertEqual(count, p.read_text().count('@Test\n'))

    def test_template_keeps_exit_allmembers_sources_static_and_no_skip(self):
        raw = target.server(); ast.parse(raw)
        for required in ["'expectedTests': 54", "'tests': 54", 'len(all_cases) == 54',
                         'members == 1643', "'expectedSuites': 7", 'images[0] == images[1]',
                         "'maven-exit.safe.json'", "'source-full-PG3350", 'umask=23',
                         'targetClassCounters', 'in all_cases']:
            self.assertIn(required, raw)
        for missing in ['skipTests', 'failIfNoSpecifiedTests', 'pausePreservingInterrupt', 'mpass010NewInterrupt']:
            self.assertNotIn(missing, raw)
        self.assertTrue(all(method in raw for _, method in target.METHODS))
        self.assertIn("env['SCHUBERT_PG_ROOT'] = str(pg)", raw)
        self.assertIn("'postgresToolchain': pg_meta", raw)
        self.assertIn("'runs/PG3366-related-v2'", raw)
        self.assertLess(raw.index("env['SCHUBERT_PG_ROOT']"), raw.index("'-Dnk.pt.repository='"))
        self.assertNotIn('PG3366-related-v1', raw)

    def test_genuine_classifier_rejects_skip_even_when_counts_are_correct(self):
        node = ET.fromstring('<testsuite name="X" tests="1" failures="0" errors="0" skipped="1"><testcase classname="X" name="one"><skipped/></testcase></testsuite>')
        with self.assertRaises(ValueError):
            target.prior.classify([node], {'X': 1})


if __name__ == '__main__':
    unittest.main()
