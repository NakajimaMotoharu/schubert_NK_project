import unittest
from pg2412_question_unused_sources import sources, BEFORE, CURRENT, CURRENT_BOM, production


class UnusedRoles(unittest.TestCase):
    def test_whole_authenticated_retired_current_and_new_question_roles(self):
        values = sources('a'*64)
        raw = values['pg2412_native_refs.py']
        for v in ['START=20469616839;END=22107644017','/proc/104841',
                  'pg2410-retired-current-before-v1', "parent_config=={'Type':'oneshot','SuccessExitStatus':'10'}"]:
            self.assertIn(v, raw)
        whole = '\n'.join(values.values())
        for v in [BEFORE,CURRENT,CURRENT_BOM,production(),'PG2428','PG2126']:
            self.assertIn(v,whole)
        for v in ['pg2130-current-normal-before-v1','pg2144-current-normal-unused-tools-v1',
                  'a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75','__NEW_QUESTION']:
            self.assertNotIn(v,whole)
        receipt=values['pg2412_parent_receipt.py']
        self.assertIn('e1429ac8-f3dd-4e8c-83d2-1926c4ba8440',receipt)
        self.assertIn('currentManagerGc',values['pg2412_warning_parent_projection.py'])

    def test_unknown_before_bom_no_emission(self):
        for bom in [None,'a'*63,'x'*64]:
            with self.assertRaises(ValueError):
                sources(bom)
        with self.assertRaises(ValueError):
            sources('a'*64,'b'*64)


if __name__ == '__main__':
    unittest.main()
