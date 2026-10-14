import unittest
from pg2538_strict_current_observer import source
from pg2540_strict_current_noargs_once import body
from pg2516_current_strict_candidate_sources import SOURCE


class NewCurrent(unittest.TestCase):
    def test_observer_exact_new_current_and_qualified_post(self):
        raw = source('a'*64)
        for marker in ['pg2538', 'PG2512', SOURCE, 'a'*64, 'pg2536-strict-normal-publication-post-v1']:
            self.assertIn(marker, raw)
        self.assertNotIn('pg2444-question-normal-publication-post-v1', raw)
        self.assertNotIn('pg2446', raw)

    def test_ordinary_once_uses_new_slot_and_preserves_actual_twenty_two_native(self):
        raw = body('a'*64)
        for marker in ['pg2540-strict-current-noargs-once-v1', 'pg2538', SOURCE,
                       'PG2512', 'require(len(records)==22)', 'declaration=exec_record']:
            self.assertIn(marker, raw)
        self.assertNotIn('require(len(records)==16)', raw)
        self.assertNotIn('pg2448-question-current-noargs-once-v1', raw)

    def test_missing_unknown_and_non_sha_bom_refused_before_any_action(self):
        for value in ['', 'x'*64, 'a'*63, False]:
            for function in [source, body]:
                with self.assertRaises(ValueError):
                    function(value)


if __name__ == '__main__':
    unittest.main()
