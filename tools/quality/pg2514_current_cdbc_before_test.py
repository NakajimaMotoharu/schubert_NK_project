import ast
import unittest
import pg1257_fresh_independent_terminal_post as schema
from pg2514_current_cdbc_before import payload, SLOT


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
        self.assertIn("flat={k:v for k,v in after.items()if k!='native'}", raw)

    def test_missing_seals_fail_closed_before_any_guest_operation(self):
        with self.assertRaises(ValueError):
            payload({})


if __name__ == '__main__':
    unittest.main()
