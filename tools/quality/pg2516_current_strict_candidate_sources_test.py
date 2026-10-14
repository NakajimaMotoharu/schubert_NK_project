import ast
import unittest
from pg2516_current_strict_candidate_sources import sources, bind, SOURCE, CURRENT, CURRENT_BOM, BEFORE, TOOLS, ARCHIVE


class CurrentRoles(unittest.TestCase):
    def test_actual_current_candidate_roles_and_exact_current_receipt(self):
        values = sources('a'*64)
        whole = '\n'.join(values.values())
        for marker in [SOURCE, CURRENT, CURRENT_BOM, BEFORE, TOOLS,
                       'pg2514-current-cdbc-before-v2', '06236d14-a6f8-4d05-a6ff-49c713cc2647',
                       'c347b14a-2e59-41e6-993c-a07e537cbd00']:
            self.assertIn(marker, whole)
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2512', values['pg2516_input_preflight.py'])
        self.assertIn('/opt/schubert-nk/releases/0.1.0-PG2428', values['Pg2516UnusedStage.java'])
        self.assertIn(ARCHIVE, whole)
        self.assertIn('GC=', values['pg2516_parent_receipt.py'])
        self.assertIn('START=29104365495;END=30827355356', values['pg2516_native_refs.py'])
        self.assertIn('/proc/194154', values['pg2516_native_refs.py'])
        self.assertIn("'Id': 'schubert-nk-morning-controller.service'", values['pg2516_warning_parent_projection.py'])
        for name, body in values.items():
            if name.endswith('.py'):
                ast.parse(body)
            self.assertNotIn('pg2410-retired-current-before-v1', body)
            for old in ['20469616839', '22107644017', '/proc/104841']:
                self.assertNotIn(old, body)

    def test_invalid_new_bom_or_before_refused(self):
        for value in [None, 'x'*64, 'a'*63]:
            with self.assertRaises(ValueError):
                sources(value)
        with self.assertRaises(ValueError):
            sources('a'*64, 'b'*64)

    def test_overlapping_release_and_source_roles_are_protected(self):
        from pg2432_current_boot_question_sources import production, CURRENT as old_current
        value = bind(production() + ' ' + old_current + ' PG2428 PG2126 pg2428 pg2126')
        self.assertEqual(SOURCE + ' ' + CURRENT + ' PG2512 PG2428 pg2512 pg2428', value)


if __name__ == '__main__':
    unittest.main()
