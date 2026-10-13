"""Whole selected source and fixed PostgreSQL isolation/immutable Main contract."""
import unittest
from pyflakes.api import check
from pg2292_morning_guard_selected import server,FILES,native_input
import pg2293_morning_guard_selected_v2 as corrected


class SelectedMorningGuard(unittest.TestCase):
    def test_actual_whole_server_uses_frozen_latest_full_and_two_tests(self):
        raw=server();self.assertEqual(0,check('INPUT={}\n'+raw,'<whole selected server>'))
        for literal in ['source-full-PG2228','tests2 failures0','tests\':\'2','len(x.findall(\'testcase\'))==2','SCHUBERT_PG_ROOT','-Dnk.pt.repository=','extra_library_hashes','classByteMismatch','MainRecompiled\':False']:
            self.assertIn(literal,raw)
        self.assertNotIn('source-full-PG2124',raw)
        self.assertNotIn('Pg2220',raw)
        self.assertEqual(4,len(FILES))
        self.assertIn('*hosts,*native_streams,str(execfile)',raw)
        self.assertIn('remainingSameSourceWithNative',raw)
        self.assertEqual(9,len(native_input()['files']))

    def test_corrected_attempt_new_namespace_same_explicit_test_suite(self):
        raw=corrected.server();self.assertEqual(0,check('INPUT={}\n'+raw,'<new corrected selected server>'))
        self.assertIn('PG2293-selected-v2',raw)
        self.assertNotIn('PG2292-selected-v1',raw)
        self.assertIn('PG2292 tests2 failures0',raw)
        self.assertIn('Pg2292MorningGuardLauncher',raw)


if __name__=='__main__':unittest.main()
