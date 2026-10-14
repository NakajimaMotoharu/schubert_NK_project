import ast
import unittest
import pg1257_fresh_independent_terminal_post as schema
from pg2514_current_cdbc_before import payload, SLOT, CURRENT_FIELDS, validate_current_image


class CurrentBefore(unittest.TestCase):
    def test_current_source_run_backup_and_original_schema_not_old_role(self):
        raw = payload({n:'a'*64 for n in schema.previous.SEALS})
        ast.parse(raw)
        for marker in [SLOT, '06236d14-a6f8-4d05-a6ff-49c713cc2647',
                       '2026-10-13T21:16:10.125382Z', 'cdbc07cdf77370d521e64de8b327da7f6752139b',
                       "'runtimeAlreadyRetired':True", "'startsStopsReloadsSqlWrites0':True"]:
            self.assertIn(marker, raw)
        self.assertNotIn("save=base/'pg2410-retired-current-before-v1'", raw)
        self.assertIn('zz-pg2316-once-resume.conf', raw)
        self.assertIn('flat=validate_current_image(after,native)', raw)
        self.assertNotIn("require(after['native']==native)", raw)

    def test_current_exact_schema_unknown_missing_native_and_null_fail_closed(self):
        original = {key: {} for key in CURRENT_FIELDS}
        self.assertIs(original, validate_current_image(original, {}))
        for wrong in [None, [], {}, {**original, 'native': {}}, {**original, 'unknown': {}}]:
            with self.assertRaises(ValueError):
                validate_current_image(wrong, {})
        for wrong in [None, [], False]:
            with self.assertRaises(ValueError):
                validate_current_image(original, wrong)

    def test_missing_seals_fail_closed_before_any_guest_operation(self):
        with self.assertRaises(ValueError):
            payload({})


if __name__ == '__main__':
    unittest.main()
