import unittest
from pyflakes.api import check
from pg2413_question_unused_compile import compiler


class Compiler(unittest.TestCase):
    def test_complete_actual_compile_graph_namespace_and_current_libraries(self):
        raw = compiler()
        prefix = ('import os,subprocess,json,hashlib,tarfile,datetime\nfrom pathlib import Path\n'
                  'from pg2413_question_unused_compile import TARGET,ARCHIVE,CURRENT,BEFORE,sources,validate_actual_graph\n'
                  'from pg2133_current_normal_unused_compile import inventory\n'
                  'from pg1642_completed_candidate_compile import W,P,J,write,sha,check_members\n'
                  'PRODUCTION="fixed"\n__file__="fixed"\n')
        # Undefined names are checked against the actual compiler imports, not a
        # shortened helper excerpt; full ABI execution is required after signing.
        compile(raw,'<all ABI source>','exec')
        for v in ['pg2413-','Pg2412NativeArgumentTest','pg2375-frozen-v1','pg2428']:
            self.assertIn(v,raw)
        self.assertNotIn('pg2133-frozen',raw)
        self.assertNotIn('pg2091-frozen',raw)
        self.assertNotIn('StartUnit(',raw)
        self.assertEqual(0,check(prefix+raw,'<complete ABI entry>'))


if __name__ == '__main__':
    unittest.main()
