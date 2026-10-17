"""Check exact SSC304 scope and generated complete namespace, not Production PT."""
import inspect
import re
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4956_expiry_success_selected as role


class ExpirySelection(unittest.TestCase):
    def test_real_git_main_scope_and_foreign_or_absent_diff_rejection(self):
        role.validate_selection()
        for changed in ('',role.MAIN_PATH+'\nsrc/schubert-nk-batch/src/main/java/Foreign.java\n'):
            with patch.object(role.subprocess,'check_output',return_value=changed):
                with self.assertRaisesRegex(ValueError,'only SSC304 Main'):role.validate_selection()

    def test_actual_scope_and_new_literal_oracles(self):
        self.assertEqual({'storage','bootstrap','batch'},set(role.MODULES.values()))
        self.assertEqual(7,len(role.MODULES))
        count=0
        for name,module in role.MODULES.items():
            path=role.ROOT/('src/schubert-nk-'+module+'/src/test/java/'+name.replace('.','/')+'.java')
            text=path.read_text();methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',text)
            self.assertEqual(text.count('@Test'),len(methods));self.assertEqual(len(methods),len(set(methods)))
            count+=len(methods)
            if name.endswith('ExpirySuccessfulScopeTest'):
                self.assertEqual(16,len(methods));self.assertTrue(all(m.startswith('exp4956')for m in methods))
                self.assertIn('try (JdbcClose owned = release::close)',text)
        self.assertGreater(count,30)

    def test_strict_complete_namespace_and_results(self):
        raw=role.source();header=inspect.getsource(role.previous.base).split('\ndef main():',1)[0]
        header+='\nMODULES={}\nMAIN_SOURCE="candidate"\nMETHODS={}\ndef verify_main_bytes(snapshot):raise ValueError("not a receipt")\n'
        self.assertEqual(0,check(header+'\n'+raw,'<complete SSC304 selection namespace>'))
        self.assertLess(raw.index('format_command='),raw.index('child = subprocess.Popen'))
        for literal in ('actual != expected','flakyFailure','ptNotRun','freshStaticModules',
                        'verify_main_bytes(snapshot)',"needed={'LINE','METHOD'}|({'BRANCH'}if name!='usingJdbc'or 'BRANCH'in count else set())"):
            self.assertIn(literal,raw)
        self.assertNotIn('-DfailIfNoTests=false',raw)
        self.assertIn("'mainDelta':main_bytes",raw)
        for path in(role.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
